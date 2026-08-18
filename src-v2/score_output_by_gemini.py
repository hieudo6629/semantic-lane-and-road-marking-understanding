"""
Chấm điểm chất lượng output LLM (từ llm_batch_client.py) bằng Gemini, dựa
trên 6 tiêu chí có trọng số, so sánh giữa nhiều thí nghiệm (prompt khác nhau).

KIẾN TRÚC: mỗi ảnh chỉ gọi Gemini ĐÚNG 1 LẦN - gộp ảnh + nội dung .txt của
TẤT CẢ thí nghiệm (EXPERIMENT_FOLDERS) vào cùng 1 prompt, nhận về 1 JSON
chứa điểm chấm cho từng thí nghiệm. (Bản trước gọi RIÊNG cho từng thí
nghiệm - N thí nghiệm = N request/ảnh, với 3 thí nghiệm x 199 ảnh = 597
request, dễ dính rate-limit hơn hẳn so với 199 request như hiện tại. Gộp
lại còn giúp Gemini đánh giá 3 output trong cùng 1 ngữ cảnh, nhất quán hơn
so với 3 lần chấm độc lập không biết gì về nhau.)

Cấu hình (đường dẫn, API key, tiêu chí, tên phiên...) nằm trong phần
CẤU HÌNH ngay bên dưới - đây là NƠI DUY NHẤT cần sửa.

Cần biến môi trường GEMINI_API_KEY trước khi chạy:
    export GEMINI_API_KEY="..."          # bash
    $env:GEMINI_API_KEY = "..."           # PowerShell
"""

import base64
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, Optional

import google.generativeai as genai
import google.api_core.exceptions as google_exceptions

from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# SỬA: mở rộng danh sách lỗi coi là TẠM THỜI (được retry) - bản trước chỉ
# bắt đúng 4 loại (ResourceExhausted/ServiceUnavailable/DeadlineExceeded/
# InternalServerError). Nếu gặp loại lỗi tạm thời KHÁC (ví dụ Aborted,
# BadGateway - hay gặp khi mạng chập chờn hoặc server Google quá tải) thì
# bản trước coi là lỗi VĨNH VIỄN và bỏ cuộc ngay, không hề thử lại - có thể
# đây là nguyên nhân khiến 1 số ảnh "chờ rất lâu thậm chí lỗi" dù đã bật
# billing. Dùng getattr(...) thay vì import thẳng tên lớp, để không bị
# ImportError nếu phiên bản SDK đang cài không có đúng tên lớp đó.
RETRYABLE_EXCEPTION_NAMES = (
    "ResourceExhausted",  # 429 - rate limit / quota
    "ServiceUnavailable",  # 503 - server quá tải
    "DeadlineExceeded",  # 504 - timeout phía server
    "InternalServerError",  # 500
    "Aborted",  # 409 - thường do xung đột tạm thời
    "BadGateway",  # 502
    "TooManyRequests",  # 429 (tên khác của ResourceExhausted ở 1 số phiên bản SDK)
)
RETRYABLE_EXCEPTIONS = tuple(
    exc_class
    for exc_class in (getattr(google_exceptions, name, None) for name in RETRYABLE_EXCEPTION_NAMES)
    if exc_class is not None
)

# ============================================================
# CẤU HÌNH - đây là NƠI DUY NHẤT cần sửa trong file này
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# "gemini-2.0-flash" đã bị Google ngừng hỗ trợ (lỗi 404 "no longer
# available"). Nếu model bên dưới sau này cũng bị đổi/ngừng hỗ trợ, lấy
# danh sách model còn khả dụng bằng đoạn sau (chạy tay, không phải chạy script này):
#     import google.generativeai as genai
#     genai.configure(api_key="...")
#     for m in genai.list_models():
#         if "generateContent" in m.supported_generation_methods:
#             print(m.name)
MODEL_NAME = "gemini-3.5-flash"

IMAGES_FOLDER = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\input"

EXPERIMENT_FOLDERS = {
    "prompt_image_json": r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\output-suggest-prompt-v2",
    "prompt_image": r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\output-suggest-image-only-prompt-v2",
    "prompt_json": r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\output-suggest-json-only-prompt-v2",
}

OUTPUT_DIR = r"C:\Users\Hieu\IdeaProjects\Semantic Traffic\semantic-road-marking-understanding\src-v2\evaluation_results"

# Tên thư mục phiên chấm điểm - CỐ ĐỊNH (không tự sinh theo timestamp như bản
# cũ) để lần chạy sau tự động RESUME (bỏ qua ảnh đã chấm) thay vì chấm lại
# từ đầu và tốn quota API mỗi khi bị lỗi/rate-limit giữa chừng. Muốn chấm 1
# phiên hoàn toàn mới: đổi tên này.
SESSION_NAME = "session_2"

# Chấm lại cả những ảnh đã có sẵn file JSON kết quả hay không.
OVERWRITE_EXISTING = False

# Thời gian chờ giữa các request (giây). Vì mỗi ảnh giờ chỉ 1 request (không
# phải 3 như trước), có thể để thấp hơn vẫn an toàn với hạn mức free tier
# (20 request/phút -> tối thiểu 3s/request); vẫn để dư biên an toàn.
DELAY_SECONDS = 4.0

# Số lần thử lại tối đa khi gặp lỗi tạm thời (rate limit/quota/server quá tải).
MAX_RETRIES = 5

# Thời gian chờ mặc định (giây) khi KHÔNG tách được retry_delay từ lỗi Google
# trả về (xem _extract_retry_delay_seconds()).
RETRY_DELAY_FALLBACK_SECONDS = 20.0

# Thời gian chờ (giây) khi Gemini trả về JSON SAI CÚ PHÁP (không phải lỗi
# rate-limit) trước khi thử lại - ngắn hơn nhiều so với RETRY_DELAY_FALLBACK_SECONDS
# vì đây chỉ là lỗi sinh sai ngẫu nhiên của model, không phải giới hạn server
# cần chờ lâu.
JSON_RETRY_DELAY_SECONDS = 3.0

EVALUATION_CRITERIA = {
    "situation_understanding": {
        "weight": 5,
        "description": "correct understanding of relevant road, traffic, and hazards.",
    },
    "road_understanding": {
        "weight": 5,
        "description": "correct road geometry, lanes, boundaries, and neighboring lanes.",
    },
    "lane_ego_position": {
        "weight": 5,
        "description": "correct ego lane, position, and offset when supported.",
    },
    "traffic_sign_rule": {
        "weight": 5,
        "description": "correct signs, signals, and explicitly supported rules/speed limits.",
    },
    "driving_recommendation": {
        "weight": 5,
        "description": "safe, appropriate, necessary, specific, and evidence-based action.",
    },
    "safety_considerations": {
        "weight": 5,
        "description": "relevant safety risks without generic or unsupported claims.",
    },
}
# LƯU Ý: trường "weight" ở trên KHÔNG còn được code dùng để tự tính điểm
# tổng nữa (đã bỏ theo yêu cầu - xem _build_evaluation_prompt()) - chỉ còn
# giữ lại làm METADATA lưu vào config.json, để người dùng biết đúng trọng số
# đã dùng khi tự tính điểm tổng sau này từ dữ liệu "scores" thô.

# Phần hướng dẫn chấm điểm CỐ ĐỊNH, đặt NGUYÊN VĂN theo đúng prompt do người
# dùng thiết kế - sửa trực tiếp tại đây khi cần đổi cách chấm. LƯU Ý: trọng
# số ghi trong đây (×3, ×5...) PHẢI khớp với "weight" trong EVALUATION_CRITERIA
# ở trên - đây là 2 nơi khai báo cùng 1 thông tin, không tự động đồng bộ với
# nhau, sửa 1 bên thì phải sửa bên kia cho khớp.
EVALUATION_INSTRUCTIONS = """You are an expert evaluator of AI traffic-scene understanding and driving recommendations.
Evaluate the 3 outputs for the SAME traffic image independently.
Use the image as the visual reference. Do NOT compare outputs when assigning scores.
Score based on correctness and evidence, not writing quality or verbosity.

Criteria:
1. situation_understanding: correct understanding of relevant road, traffic, and hazards.
2. road_understanding: correct road geometry, lanes, boundaries, and neighboring lanes.
3. lane_ego_position: correct ego lane, position, and offset when supported.
4. traffic_sign_rule: correct signs, signals, and explicitly supported rules/speed limits.
5. driving_recommendation: safe, appropriate, necessary, specific, and evidence-based action.
6. safety_considerations: relevant safety risks without generic or unsupported claims.
All six criteria are equally weighted.
Each criterion is scored independently from 1 to 5.
The maximum score is 5 for every criterion.
Do not apply different weights between criteria.
Scoring:
5 = Correct and complete; no meaningful errors.
4 = Mostly correct; minor non-critical errors or omissions.
3 = Partially correct; noticeable errors, but main situation is understood.
2 = Major errors that affect the assessment.
1 = Incorrect, unsupported, or unusable.

Important:
- Unsupported assumptions or hallucinations reduce the relevant score.
- Do not reward extra detail or verbosity.
- Do not penalize omission of information that is irrelevant to the driving decision.
- Do not infer speed limits, signs, hazards, or traffic conditions without evidence.
- Evaluate each criterion only from information relevant to that criterion.
- Give one concise sentence explaining each score."""

# ============================================================
# HÀM ĐỌC FILE / TIỆN ÍCH
# ============================================================


def read_text_file(file_path: str) -> str:
    """Đọc nội dung file text."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.warning(f"Lỗi đọc file {file_path}: {e}")
        return ""


def _guess_mime_type(image_path: str) -> str:
    """Suy ra mime type từ phần mở rộng file (không hardcode "image/jpeg" cho mọi ảnh)."""
    ext = os.path.splitext(image_path)[1].lstrip(".").lower()
    return "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'jpeg'}"


def _safe_score(raw_value, criterion_key: str) -> float:
    """
    Ép giá trị score Gemini trả về sang float một cách an toàn.

    Nếu Gemini lỡ trả score dạng chuỗi (ví dụ "4" thay vì 4), sum(scores)
    tính điểm trung bình sau đó sẽ ném TypeError nếu không ép kiểu trước -
    lỗi này sẽ làm crash toàn bộ script giữa batch nếu không được xử lý ở đây.
    """
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        logger.warning(f"Giá trị score không hợp lệ cho '{criterion_key}': {raw_value!r} - dùng 0.0")
        return 0.0


def _extract_score_value(entry):
    """
    Lấy giá trị score thô từ 1 mục trong result[exp_name]['scores'][key].

    Phòng trường hợp Gemini lệch cấu trúc (trả thẳng số thay vì dict
    {"score": .., "comment": ..} cho 1 tiêu chí nào đó) - .get() trên 1 số sẽ
    ném AttributeError nếu không kiểm tra kiểu trước.
    """
    if isinstance(entry, dict):
        return entry.get("score", 0)
    return entry


def _accumulate_scores(exp_result: Dict, scores_accumulator: Dict[str, list]) -> None:
    """Cộng dồn điểm từng tiêu chí của 1 kết quả đánh giá (1 thí nghiệm, 1 ảnh) vào bộ tích lũy dùng để tính trung bình."""
    scores = exp_result.get("scores", {}) if isinstance(exp_result, dict) else {}
    for key in EVALUATION_CRITERIA:
        if key in scores:
            score = _safe_score(_extract_score_value(scores[key]), key)
            scores_accumulator[key].append(score)


def _extract_retry_delay_seconds(exc: Exception, default: float) -> float:
    """
    Lấy số giây cần chờ trước khi thử lại, từ lỗi rate-limit/quota Google trả về.

    Google trả kèm gợi ý thời gian chờ chính xác (ví dụ "retry_delay { seconds: 31 }"
    hoặc "Please retry in 31.87s") - ưu tiên dùng đúng giá trị này thay vì đoán.
    Thử qua thuộc tính retry_delay trước (một số phiên bản SDK có sẵn), nếu
    không có thì parse trực tiếp từ nội dung lỗi bằng regex.
    """
    retry_delay = getattr(exc, "retry_delay", None)
    if retry_delay is not None:
        seconds = getattr(retry_delay, "seconds", None)
        if seconds is not None:
            return float(seconds) + 1.0  # +1s đệm an toàn

    message = str(exc)
    match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", message)
    if match:
        return float(match.group(1)) + 1.0

    match = re.search(r"retry in ([\d.]+)\s*s", message, re.IGNORECASE)
    if match:
        return float(match.group(1)) + 1.0

    return default


# ============================================================
# HÀM GỌI GEMINI API
# ============================================================


def _build_evaluation_prompt(experiment_outputs: Dict[str, str]) -> str:
    """
    Dựng prompt đánh giá ĐỒNG THỜI nhiều thí nghiệm trong 1 lần gọi.

    Phần hướng dẫn chấm điểm (EVALUATION_INSTRUCTIONS) là NGUYÊN VĂN do người
    dùng thiết kế, không tự sinh từ EVALUATION_CRITERIA nữa. Chỉ còn phần
    liệt kê output cần chấm + yêu cầu cấu trúc JSON trả về là dựng ĐỘNG theo
    đúng tên thí nghiệm trong experiment_outputs (không hardcode tên/số
    lượng thí nghiệm cụ thể).
    """
    outputs_block = "\n\n".join(
        f"--- Experiment: {name} ---\n{output}" for name, output in experiment_outputs.items()
    )

    # SỬA: BỎ HẲN việc tính total_score (cả ở Gemini lẫn ở code) - Gemini là
    # LLM, không phải máy tính, dễ cộng sai đúng lúc cần chính xác nhất, lại
    # tốn thêm token sinh ra bước tính toán đó. Script giờ chỉ xuất "scores"
    # thô (6 điểm/tiêu chí + nhận xét) cho từng thí nghiệm - việc tính điểm
    # tổng (theo công thức trọng số nào, gộp bao nhiêu ảnh...) để người dùng
    # tự làm sau từ dữ liệu thô này, tùy ý muốn thay đổi công thức mà không
    # cần sửa lại script.
    scores_schema = ",\n      ".join(
        f'"{key}": {{"score": 0, "comment": "..."}}' for key in EVALUATION_CRITERIA
    )
    experiment_schema = (
        "{\n"
        f"      \"scores\": {{\n      {scores_schema}\n      }},\n"
        "      \"overall_comment\": \"...\"\n"
        "    }"
    )
    schema_block = ",\n".join(f'  "{name}": {experiment_schema}' for name in experiment_outputs)

    return f"""{EVALUATION_INSTRUCTIONS}

### INPUT IMAGE
[See attached image]

### OUTPUTS TO EVALUATE (one per experiment, same image)
{outputs_block}

### OUTPUT FORMAT
Respond in English. Return EXACTLY the following JSON structure - one top-level key per experiment name listed above. All 6 "score" fields must be integers from 1 to 5. Do not compute or include any total/aggregate score.

{{
{schema_block}
}}
"""


def call_gemini_evaluate(
    image_path: str,
    experiment_outputs: Dict[str, str],
    model: "genai.GenerativeModel",
) -> Optional[Dict[str, Dict]]:
    """
    Gọi Gemini MỘT LẦN để đánh giá đồng thời output của NHIỀU thí nghiệm
    (cùng 1 ảnh), dựa trên 6 tiêu chí.

    Returns:
        Dict với 1 key cho mỗi tên thí nghiệm trong experiment_outputs, mỗi
        giá trị có dạng {"scores": {...}, "overall_comment": ..} (KHÔNG có
        điểm tổng - xem _build_evaluation_prompt()), hoặc None nếu gọi API
        thất bại sau khi đã thử lại.
    """
    prompt = _build_evaluation_prompt(experiment_outputs)

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_part = {"mime_type": _guess_mime_type(image_path), "data": base64.b64encode(image_data).decode("utf-8")}
    except OSError as e:
        logger.warning(f"Lỗi đọc ảnh {image_path}: {e}")
        return None

    # Cơ chế delay + retry cho lỗi rate-limit/quota (429 ResourceExhausted) và
    # các lỗi tạm thời khác (503/504/500), cộng với retry khi Gemini trả JSON
    # sai cú pháp (response_mime_type giảm nhưng không loại bỏ hoàn toàn khả
    # năng này). Các lỗi KHÁC (API key sai, ảnh hỏng...) không retry.
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [prompt, image_part],
                generation_config={
                    "temperature": 0.1,
                    # Response giờ gộp N thí nghiệm trong 1 lần (N x 6 tiêu
                    # chí x comment) nên cần budget token lớn hơn nhiều so
                    # với khi chỉ chấm 1 thí nghiệm/request - tăng lên 8192
                    # để giảm rủi ro bị cắt cụt giữa chừng.
                    "max_output_tokens": 8192,
                    # Ép Gemini trả JSON THUẦN thay vì phải tự dò bằng regex
                    # (regex tham lam dễ khớp sai nếu response có thêm chữ
                    # chứa dấu ngoặc nhọn trước/sau khối JSON thật).
                    "response_mime_type": "application/json",
                },
            )
            return json.loads(response.text.strip())
        except json.JSONDecodeError as e:
            # response_mime_type="application/json" giảm nhưng không loại bỏ
            # hoàn toàn khả năng Gemini tự sinh JSON sai cú pháp (ví dụ dấu "
            # không được escape đúng trong 1 câu comment tự do). Đây là lỗi
            # sinh NGẪU NHIÊN của model, không phải lỗi hệ thống - thử lại
            # (model sinh lại từ đầu) thường tự khỏi.
            context_start = max(0, e.pos - 150)
            context_end = min(len(response.text), e.pos + 150)
            snippet = response.text[context_start:context_end]
            if attempt >= MAX_RETRIES:
                logger.error(f"Hết {MAX_RETRIES} lần thử do Gemini liên tục trả JSON sai cú pháp: {e}. Đoạn quanh lỗi: ...{snippet}...")
                return None
            logger.warning(
                f"[Thử lại {attempt}/{MAX_RETRIES}] Response không phải JSON hợp lệ ({e}), thử lại sau "
                f"{JSON_RETRY_DELAY_SECONDS:.0f}s. Đoạn quanh vị trí lỗi: ...{snippet}..."
            )
            time.sleep(JSON_RETRY_DELAY_SECONDS)
        except RETRYABLE_EXCEPTIONS as e:
            if attempt >= MAX_RETRIES:
                logger.error(f"Hết {MAX_RETRIES} lần thử do lỗi tạm thời ({type(e).__name__}): {e}")
                return None
            wait_seconds = _extract_retry_delay_seconds(e, default=RETRY_DELAY_FALLBACK_SECONDS)
            logger.warning(
                f"[Thử lại {attempt}/{MAX_RETRIES}] Lỗi tạm thời từ Gemini ({type(e).__name__}), "
                f"chờ {wait_seconds:.0f}s rồi thử lại: {e}"
            )
            time.sleep(wait_seconds)
        except Exception as e:  # noqa: BLE001 - lỗi khác (không phải rate-limit/JSON) không được làm dừng cả batch
            # SỬA: log thêm type(e).__name__ - nếu đây thực ra là 1 loại lỗi
            # TẠM THỜI khác mà RETRYABLE_EXCEPTIONS chưa liệt kê (ví dụ lỗi
            # timeout phía transport/mạng, không phải lớp con của
            # google.api_core.exceptions), tên lớp chính xác ở đây giúp biết
            # ngay cần thêm gì vào RETRYABLE_EXCEPTION_NAMES mà không cần đoán.
            logger.error(f"Lỗi gọi Gemini ({type(e).__name__}): {e}")
            return None

    return None


# ============================================================
# HÀM CHÍNH: CHẤM ĐIỂM TOÀN BỘ
# ============================================================


def evaluate_all_experiments(
    images_folder: str,
    experiment_folders: Dict[str, str],
    output_dir: str,
    api_key: str,
    model_name: str = MODEL_NAME,
    session_name: str = "session_1",
    overwrite_existing: bool = False,
    delay: float = DELAY_SECONDS,
) -> Dict:
    """
    Chấm điểm tất cả ảnh, mỗi ảnh 1 lần gọi Gemini gộp toàn bộ thí nghiệm.

    Lưu 1 file JSON theo tên ảnh: <tên_ảnh>.json (chứa kết quả của TẤT CẢ
    thí nghiệm cho ảnh đó), thay vì 1 file JSON riêng mỗi (ảnh, thí nghiệm)
    như bản trước.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    logger.info(f"Đã kết nối Gemini ({model_name})")

    if not os.path.isdir(images_folder):
        logger.error(f"Không tìm thấy thư mục ảnh: {images_folder}")
        return {}
    logger.info(f"Thư mục ảnh: {images_folder}")

    # Kiểm tra thư mục thí nghiệm NGAY TỪ ĐẦU (không phải trong lúc chạy) -
    # vì giờ 1 request gộp CẢ N thí nghiệm/ảnh, thiếu 1 thư mục nghĩa là
    # KHÔNG THỂ tạo request hợp lệ cho bất kỳ ảnh nào nữa nếu không loại nó
    # ra trước, nên cần biết rõ ngay từ đầu thí nghiệm nào thực sự tham gia.
    valid_experiment_folders = {}
    for exp_name, exp_folder in experiment_folders.items():
        if os.path.isdir(exp_folder):
            valid_experiment_folders[exp_name] = exp_folder
        else:
            logger.warning(f"Thư mục thí nghiệm không tồn tại, bỏ qua: {exp_name} ({exp_folder})")

    if not valid_experiment_folders:
        logger.error("Không có thư mục thí nghiệm nào hợp lệ.")
        return {}

    session_dir = os.path.join(output_dir, session_name)
    os.makedirs(session_dir, exist_ok=True)
    logger.info(f"Lưu kết quả tại: {session_dir}")

    config = {
        "model": model_name,
        "session_name": session_name,
        "criteria": EVALUATION_CRITERIA,
        "images_folder": images_folder,
        "experiments": valid_experiment_folders,
    }
    with open(os.path.join(session_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    image_files = sorted(f for f in os.listdir(images_folder) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    logger.info(f"Tìm thấy {len(image_files)} ảnh, {len(valid_experiment_folders)} thí nghiệm: {list(valid_experiment_folders)}")

    exp_scores: Dict[str, Dict[str, list]] = {
        exp: {key: [] for key in EVALUATION_CRITERIA} for exp in valid_experiment_folders
    }
    exp_evaluated_count: Dict[str, int] = {exp: 0 for exp in valid_experiment_folders}

    for i, image_file in enumerate(image_files, start=1):
        base_name = os.path.splitext(image_file)[0]
        combined_json_path = os.path.join(session_dir, f"{base_name}.json")

        logger.info(f"[{i}/{len(image_files)}] {image_file}")

        # Resume: bỏ qua ảnh đã chấm ĐỦ cho TẤT CẢ thí nghiệm ở lần chạy
        # trước, trừ khi overwrite_existing=True.
        if os.path.exists(combined_json_path) and not overwrite_existing:
            try:
                cached = json.loads(read_text_file(combined_json_path) or "{}")
            except json.JSONDecodeError as e:
                # File cache cũ có thể hỏng (chạy trước bị ngắt giữa chừng lúc
                # đang ghi file, hoặc bị sửa tay) - không bắt lỗi ở đây sẽ làm
                # CRASH TOÀN BỘ script ngay khi resume.
                logger.warning(f"  File cache hỏng ({base_name}.json): {e} - sẽ chấm lại")
                cached = None

            if cached is not None and all(exp in cached for exp in valid_experiment_folders):
                logger.info(f"  Bỏ qua (đã có đủ kết quả {len(valid_experiment_folders)} thí nghiệm): {base_name}.json")
                for exp_name in valid_experiment_folders:
                    _accumulate_scores(cached[exp_name], exp_scores[exp_name])
                    exp_evaluated_count[exp_name] += 1
                continue

        # Đọc output CỦA TẤT CẢ thí nghiệm cho ảnh này - nếu thiếu bất kỳ
        # thí nghiệm nào, bỏ qua cả ảnh (không thể so sánh thiếu 1 vế).
        experiment_outputs: Dict[str, str] = {}
        missing_experiments = []
        for exp_name, exp_folder in valid_experiment_folders.items():
            txt_path = os.path.join(exp_folder, f"{base_name}.txt")
            content = read_text_file(txt_path) if os.path.exists(txt_path) else ""
            if content:
                experiment_outputs[exp_name] = content
            else:
                missing_experiments.append(exp_name)

        if missing_experiments:
            logger.warning(f"  Thiếu output ở {len(missing_experiments)} thí nghiệm ({missing_experiments}) - bỏ qua ảnh này")
            continue

        image_path = os.path.join(images_folder, image_file)

        logger.info(f"  Đang chấm điểm ({len(experiment_outputs)} thí nghiệm cùng lúc)...")
        result = call_gemini_evaluate(image_path, experiment_outputs, model)

        if result and all(
            exp in result and isinstance(result[exp], dict) and "scores" in result[exp]
            for exp in experiment_outputs
        ):
            for exp_name in experiment_outputs:
                result[exp_name]["image"] = image_file
                result[exp_name]["file"] = f"{exp_name}/{base_name}.txt"
            result["_evaluated_at"] = datetime.now().isoformat()

            with open(combined_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            for exp_name in experiment_outputs:
                _accumulate_scores(result[exp_name], exp_scores[exp_name])
                exp_evaluated_count[exp_name] += 1

            logger.info(f"  Đã chấm xong -> {base_name}.json ({len(experiment_outputs)} thí nghiệm)")
        else:
            logger.error("  Lỗi khi chấm điểm hoặc response thiếu thí nghiệm")

        if i < len(image_files):
            time.sleep(delay)

    # --- Tổng hợp kết quả theo từng thí nghiệm ---
    all_results: Dict[str, Dict] = {}
    all_raw_scores: Dict[str, list] = {key: [] for key in EVALUATION_CRITERIA}

    # SỬA: BỎ hẳn việc tự tính điểm tổng có trọng số (weighted_total_score) ở
    # đây - theo yêu cầu, việc tính điểm tổng để người dùng tự làm sau (tùy
    # công thức muốn dùng) từ dữ liệu "scores" thô đã lưu trong từng file
    # <ảnh>.json. Script chỉ còn xuất average_scores (điểm trung bình THEO
    # TỪNG TIÊU CHÍ riêng lẻ, thang 1-5) để tiện xem nhanh, không gộp thành
    # 1 con số tổng duy nhất nữa.
    for exp_name in valid_experiment_folders:
        avg_scores = {key: (sum(v) / len(v) if v else 0.0) for key, v in exp_scores[exp_name].items()}
        all_results[exp_name] = {
            "experiment": exp_name,
            "total_evaluated": exp_evaluated_count[exp_name],
            "average_scores": avg_scores,
        }
        for key, values in exp_scores[exp_name].items():
            all_raw_scores[key].extend(values)

        logger.info(f"KẾT QUẢ THÍ NGHIỆM {exp_name}: {exp_evaluated_count[exp_name]} mẫu")
        for key, val in avg_scores.items():
            logger.info(f"  - {key}: {val:.2f}")

    overall_avg = {key: (sum(v) / len(v) if v else 0.0) for key, v in all_raw_scores.items()}

    final_summary = {
        "session_name": session_name,
        "total_experiments": len(all_results),
        "overall_average_scores": overall_avg,
        "experiment_results": all_results,
    }
    with open(os.path.join(session_dir, "_final_summary.json"), "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2, ensure_ascii=False)

    logger.info("=" * 80)
    logger.info("BẢNG TỔNG HỢP KẾT QUẢ (điểm trung bình theo từng tiêu chí, thang 1-5)")
    logger.info("=" * 80)
    header = f"{'Thí nghiệm':<20} | " + " | ".join(f"{k[:14]:<14}" for k in EVALUATION_CRITERIA)
    logger.info(header)
    for exp_name, summary in all_results.items():
        scores = summary.get("average_scores", {})
        row = f"{exp_name:<20} | " + " | ".join(f"{scores.get(k, 0):<14.2f}" for k in EVALUATION_CRITERIA)
        logger.info(row)

    logger.info(f"Hoàn thành! Kết quả lưu tại: {session_dir}")

    return all_results


# ============================================================
# CHẠY SCRIPT
# ============================================================

if __name__ == "__main__":
    setup_logging()

    if not GEMINI_API_KEY:
        logger.error(
            "Thiếu GEMINI_API_KEY - đặt biến môi trường GEMINI_API_KEY trước khi chạy "
            '(export GEMINI_API_KEY="..." hoặc $env:GEMINI_API_KEY="...")'
        )
    else:
        evaluate_all_experiments(
            images_folder=IMAGES_FOLDER,
            experiment_folders=EXPERIMENT_FOLDERS,
            output_dir=OUTPUT_DIR,
            api_key=GEMINI_API_KEY,
            model_name=MODEL_NAME,
            session_name=SESSION_NAME,
            overwrite_existing=OVERWRITE_EXISTING,
            delay=DELAY_SECONDS,
        )
