"""
Chấm điểm ĐỘC LẬP từng biến thể prompt bằng Gemini - khác với
score_output_by_gemini.py/evaluate_prompt_ablation.py (gộp nhiều thí nghiệm
vào 1 lệnh gọi/ảnh), script này gọi Gemini RIÊNG cho từng ảnh, chỉ gửi kèm
ĐÚNG 1 output của ĐÚNG 1 biến thể mỗi lần - loại bỏ hoàn toàn khả năng
Gemini bị ảnh hưởng ngầm (anchoring) bởi các biến thể khác trong cùng ngữ
cảnh, đổi lại tốn 200 lệnh gọi/biến thể thay vì 200 lệnh gọi dùng chung.

Dùng cho thí nghiệm so sánh độ phức tạp prompt (current/p1_minimal/
p2_minimal_structured, xem evaluate_prompt_ablation.py) - "current" đã có
điểm sẵn từ thí nghiệm gốc nên KHÔNG chấm lại ở đây, script này chỉ chấm
p1_minimal và p2_minimal_structured.

Kết quả ghi vào evaluation_results/session_prompt_ablation_independent/
<tên_ảnh>.json, mỗi file gộp theo TÊN ẢNH (không theo biến thể) - chạy cho
p1 xong rồi chạy cho p2 sẽ THÊM key "p2_minimal_structured" vào các file đã
có key "p1_minimal", không ghi đè - nên chạy p1 xong mới chạy p2 là an toàn,
không cần chạy theo thứ tự cố định.

Cần biến môi trường GEMINI_API_KEY trước khi chạy:
    export GEMINI_API_KEY="..."          # bash
    $env:GEMINI_API_KEY = "..."           # PowerShell

Chạy (từ thư mục src-v2):
    python score_independent.py --which p1
    python score_independent.py --which p2
"""

import argparse
import base64
import json
import os
import time
from datetime import datetime
from typing import Dict, Optional

import google.generativeai as genai

from score_output_by_gemini import (
    EVALUATION_CRITERIA,
    GEMINI_API_KEY,
    MODEL_NAME,
    OUTPUT_DIR,
    RETRYABLE_EXCEPTIONS,
    JSON_RETRY_DELAY_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY_FALLBACK_SECONDS,
    _accumulate_scores,
    _extract_retry_delay_seconds,
    _guess_mime_type,
    read_text_file,
)
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, "input")

# Ánh xạ --which sang (tên biến thể, thư mục output VLM).
VARIANTS = {
    "current": ("current", os.path.join(BASE_DIR, "output-suggest-image-json-prompt-v5-31b")),
    "p1": ("p1_minimal", os.path.join(BASE_DIR, "output-prompt-ablation-p1")),
    "p2": ("p2_minimal_structured", os.path.join(BASE_DIR, "output-prompt-ablation-p2")),
}

SESSION_NAME = "session_prompt_ablation_independent"

# Hướng dẫn chấm điểm CHO 1 OUTPUT DUY NHẤT - rút gọn từ
# score_output_by_gemini.EVALUATION_INSTRUCTIONS, bỏ toàn bộ phần giả định có
# NHIỀU thí nghiệm trong cùng ngữ cảnh (không còn đúng khi chấm độc lập từng
# cái), giữ nguyên tiêu chí/thang điểm/luật chấm.
EVALUATION_INSTRUCTIONS_SINGLE = """You are an expert evaluator of LLM-based traffic decision support.

Use the original image as the visual reference for factual correctness.

The evaluation focuses specifically on road/lane/sign understanding and how this information supports the driving decision.

Criteria:

1. situation_understanding
Correct understanding of relevant road, traffic, and hazards.

2. road_understanding
Correct road geometry, lanes, boundaries, and neighboring lanes.

3. lane_ego_position
Correct ego lane, position, and offset when supported by the available evidence.

4. traffic_sign_rule
Correct signs, signals, and explicitly supported rules/speed limits.

5. driving_recommendation
Safe, appropriate, necessary, specific, and evidence-based action.

6. safety_considerations
Relevant safety risks without generic or unsupported claims.

All six criteria are equally weighted.

Each criterion is scored independently from 1 to 5.

Scoring:

5 = Correct and well supported; no meaningful error.
4 = Mostly correct; only minor non-critical errors or omissions.
3 = Partially correct; noticeable error or omission, but the main understanding remains usable.
2 = Major error that affects scene understanding or the driving decision.
1 = Incorrect, unsupported, or unusable.

Important evaluation rules:

- Score correctness and evidence, not writing quality or verbosity.
- Unsupported claims and hallucinations reduce the relevant score.
- Do not reward generic safety advice.
- Do not infer a speed limit without explicit evidence.
- Do not treat missing or undetected information as proof that an object does not exist.
- Evaluate each criterion independently.
- A correct recommendation does not automatically mean the scene understanding is correct.
- Correctly describing scene information does not automatically mean the driving recommendation is correct.
- For driving_recommendation, check whether relevant road/lane/ego/sign evidence actually supports the recommendation.
- Give one concise sentence explaining each score.
- Do not reward or penalize the output merely for following a particular response format or being more or less structured."""


def _build_single_eval_prompt(output_text: str) -> str:
    scores_schema = ",\n  ".join(f'"{key}": {{"score": 0, "comment": "..."}}' for key in EVALUATION_CRITERIA)
    return f"""{EVALUATION_INSTRUCTIONS_SINGLE}

### INPUT IMAGE
[See attached image]

### OUTPUT TO EVALUATE
{output_text}

### OUTPUT FORMAT
Respond in English. Return EXACTLY the following JSON structure. All 6 "score" fields must be integers from 1 to 5.

{{
  {scores_schema}
}}
"""


def call_gemini_score_single(image_path: str, output_text: str, model: "genai.GenerativeModel") -> Optional[Dict]:
    """Gọi Gemini MỘT LẦN, chấm ĐÚNG 1 output, không kèm output nào khác trong ngữ cảnh."""
    prompt = _build_single_eval_prompt(output_text)

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
    except OSError as e:
        logger.warning(f"Lỗi đọc ảnh {image_path}: {e}")
        return None

    image_part = {"mime_type": _guess_mime_type(image_path), "data": base64.b64encode(image_data).decode("utf-8")}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(
                [prompt, image_part],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
            )
            return json.loads(response.text.strip())
        except json.JSONDecodeError as e:
            if attempt >= MAX_RETRIES:
                logger.error(f"Hết {MAX_RETRIES} lần thử do Gemini liên tục trả JSON sai cú pháp: {e}")
                return None
            logger.warning(f"[Thử lại {attempt}/{MAX_RETRIES}] Response không phải JSON hợp lệ ({e}), thử lại sau {JSON_RETRY_DELAY_SECONDS:.0f}s.")
            time.sleep(JSON_RETRY_DELAY_SECONDS)
        except RETRYABLE_EXCEPTIONS as e:
            if attempt >= MAX_RETRIES:
                logger.error(f"Hết {MAX_RETRIES} lần thử do lỗi tạm thời ({type(e).__name__}): {e}")
                return None
            wait_seconds = _extract_retry_delay_seconds(e, default=RETRY_DELAY_FALLBACK_SECONDS)
            logger.warning(f"[Thử lại {attempt}/{MAX_RETRIES}] Lỗi tạm thời từ Gemini ({type(e).__name__}), chờ {wait_seconds:.0f}s rồi thử lại: {e}")
            time.sleep(wait_seconds)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Lỗi gọi Gemini ({type(e).__name__}): {e}")
            return None

    return None


def evaluate_variant_independent(
    variant_name: str,
    variant_folder: str,
    images_folder: str,
    session_dir: str,
    api_key: str,
    model_name: str = MODEL_NAME,
    delay: float = 4.0,
    overwrite_existing: bool = False,
) -> None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    logger.info(f"Đã kết nối Gemini ({model_name}) - chấm độc lập biến thể '{variant_name}'")

    os.makedirs(session_dir, exist_ok=True)

    # Chỉ lấy các ảnh THỰC SỰ có output của biến thể này - images_folder (input/) chứa
    # cả 200 ảnh CULane lẫn 200 ảnh real-life, nhưng variant_folder chỉ có output cho
    # đúng 200 ảnh CULane dùng trong thí nghiệm ablation này.
    all_images = sorted(f for f in os.listdir(images_folder) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    image_files = [
        f for f in all_images
        if os.path.exists(os.path.join(variant_folder, f"{os.path.splitext(f)[0]}.txt"))
    ]
    logger.info(f"Tìm thấy {len(image_files)} ảnh có output cho '{variant_name}' (trong tổng {len(all_images)} ảnh ở {images_folder})")

    scores_accum: Dict[str, list] = {key: [] for key in EVALUATION_CRITERIA}
    evaluated_count = 0

    for i, image_file in enumerate(image_files, start=1):
        base_name = os.path.splitext(image_file)[0]
        combined_json_path = os.path.join(session_dir, f"{base_name}.json")

        # Đọc file kết quả đã có của ảnh này (nếu có, từ biến thể khác chấm trước) để MERGE, không ghi đè.
        existing: Dict = {}
        if os.path.exists(combined_json_path):
            try:
                existing = json.loads(read_text_file(combined_json_path) or "{}")
            except json.JSONDecodeError as e:
                logger.warning(f"  File cache hỏng ({base_name}.json): {e} - sẽ chấm lại")
                existing = {}

        if variant_name in existing and not overwrite_existing:
            logger.info(f"[{i}/{len(image_files)}] Bỏ qua (đã có điểm '{variant_name}'): {base_name}.json")
            _accumulate_scores(existing[variant_name], scores_accum)
            evaluated_count += 1
            continue

        txt_path = os.path.join(variant_folder, f"{base_name}.txt")
        output_text = read_text_file(txt_path) if os.path.exists(txt_path) else ""
        if not output_text:
            logger.warning(f"[{i}/{len(image_files)}] Thiếu output cho {base_name} ở {variant_folder} - bỏ qua")
            continue

        image_path = os.path.join(images_folder, image_file)
        logger.info(f"[{i}/{len(image_files)}] Đang chấm độc lập '{variant_name}': {image_file}")

        result = call_gemini_score_single(image_path, output_text, model)

        if result and "scores" not in result:
            # Model có thể trả thẳng object tiêu chí không bọc trong "scores" - chuẩn hóa lại.
            result = {"scores": result}

        if result and isinstance(result, dict) and "scores" in result:
            result["image"] = image_file
            result["file"] = f"{variant_name}/{base_name}.txt"
            result["_evaluated_at"] = datetime.now().isoformat()

            existing[variant_name] = result
            with open(combined_json_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            _accumulate_scores(result, scores_accum)
            evaluated_count += 1
            logger.info(f"  Đã chấm xong -> {base_name}.json ['{variant_name}']")
        else:
            logger.error(f"  Lỗi khi chấm điểm '{variant_name}' cho {image_file}")

        if i < len(image_files):
            time.sleep(delay)

    avg_scores = {key: (sum(v) / len(v) if v else 0.0) for key, v in scores_accum.items()}
    logger.info("=" * 60)
    logger.info(f"KẾT QUẢ CHẤM ĐỘC LẬP '{variant_name}': {evaluated_count}/{len(image_files)} ảnh")
    for key, val in avg_scores.items():
        logger.info(f"  - {key}: {val:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chấm điểm độc lập (không gộp) 1 biến thể prompt bằng Gemini")
    parser.add_argument("--which", choices=list(VARIANTS), required=True, help="p1 hoặc p2")
    parser.add_argument("--overwrite", action="store_true", help="Chấm lại cả những ảnh đã có điểm cho biến thể này")
    parser.add_argument("--delay", type=float, default=4.0, help="Thời gian chờ giữa các request (giây)")
    args = parser.parse_args()

    setup_logging()

    if not GEMINI_API_KEY:
        logger.error("Thiếu GEMINI_API_KEY - đặt biến môi trường GEMINI_API_KEY trước khi chạy.")
        return

    variant_name, variant_folder = VARIANTS[args.which]
    if not os.path.isdir(variant_folder):
        logger.error(f"Chưa có output VLM cho '{variant_name}' ở {variant_folder} - chạy llm_batch_client.py sinh output trước.")
        return

    session_dir = os.path.join(OUTPUT_DIR, SESSION_NAME)
    evaluate_variant_independent(
        variant_name=variant_name,
        variant_folder=variant_folder,
        images_folder=IMAGES_FOLDER,
        session_dir=session_dir,
        api_key=GEMINI_API_KEY,
        delay=args.delay,
        overwrite_existing=args.overwrite,
    )


if __name__ == "__main__":
    main()
