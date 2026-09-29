"""
Gọi LLM hàng loạt qua NVIDIA NIM (integrate.api.nvidia.com, model
nvidia/llama-3.1-nemotron-nano-vl-8b-v1) để lấy response cho từng cặp
ảnh/JSON, lưu kết quả ra file .txt.

Hỗ trợ 3 chế độ (chọn bằng --mode):
    image_only  : chỉ gửi ẢNH + prompt (không kèm JSON)
    json_only   : chỉ gửi prompt có NHÚNG JSON (không kèm ảnh)
    image_json  : gửi cả ẢNH và prompt có NHÚNG JSON

Ảnh (<tên>.jpg) và JSON (<tên>.json, dùng để liệt kê danh sách ảnh cần xử lý)
nằm ở 2 thư mục riêng, khớp nhau theo tên file (không phần mở rộng). Nội dung
THỰC SỰ gửi cho LLM ở chế độ json_only/image_json là <tên>_brief.json (JSON
RÚT GỌN, cùng thư mục --json-dir), không phải <tên>.json thô - xem
process_one(). Output lưu vào thư mục thứ 3, mỗi mục 1 file <tên>.txt (+ 1
file _summary.json tổng hợp toàn batch).

Cần biến môi trường NVIDIA_API_KEY (hoặc truyền --api-key) trước khi chạy:
    export NVIDIA_API_KEY="nvapi-..."          # bash
    $env:NVIDIA_API_KEY = "nvapi-..."           # PowerShell

PROMPT: hardcode trong DEFAULT_PROMPTS (bên dưới) theo từng --mode - sửa
trực tiếp trong file này khi cần đổi nội dung, KHÔNG cần truyền --prompt mỗi
lần chạy. Chỉ dùng --prompt/--prompt-file khi muốn ghi đè tạm thời để thử
nhanh 1 prompt khác. Trong prompt có placeholder {json} để chỉ định CHÍNH
XÁC vị trí chèn JSON - nếu không có placeholder này, JSON sẽ tự động được
nối thêm vào cuối prompt trong 1 khối ```json ... ```.

Ví dụ (dùng thẳng prompt hardcode, không cần --prompt):
    # 1. Chỉ ảnh + prompt
    python llm_batch_client.py --mode image_only \\
        --image-dir path/to/images --output-dir path/to/out

    # 2. Chỉ prompt chứa JSON
    python llm_batch_client.py --mode json_only \\
        --json-dir path/to/json --output-dir path/to/out

    # 3. Ảnh + prompt chứa JSON
    python llm_batch_client.py --mode image_json \\
        --image-dir path/to/images --json-dir path/to/json --output-dir path/to/out
"""

import argparse
import base64
import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import cv2
import requests

from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# API NVIDIA NIM trực tiếp - KHÔNG qua fcc-server. Model không có tiền tố
# "nvidia_nim/" (tiền tố đó chỉ dùng khi route qua 1 gateway kiểu LiteLLM,
# gọi thẳng NVIDIA thì dùng đúng model id của họ).
DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/ising-calibration-1.5-31b"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Prompt mặc định cho từng --mode - SỬA TRỰC TIẾP TẠI ĐÂY khi cần đổi nội
# dung (prompt khá dài nên hardcode thay vì phải truyền --prompt mỗi lần
# chạy). Vẫn có thể ghi đè tạm thời bằng --prompt/--prompt-file nếu chỉ
# muốn thử nhanh 1 prompt khác mà không sửa file.
DEFAULT_PROMPTS = {
    "common":"""
You are a traffic scene understanding and decision-support assistant.

Your task is to understand the road and lane configuration, ego-vehicle position, traffic signs, and other decision-relevant information from the provided evidence, then provide a safe, objective, concise, and evidence-based driving recommendation.

1. EVIDENCE

- Use ONLY information supported by the provided evidence.
- Do not invent or assume vehicles, lanes, lane boundaries, road markings, traffic signs, signals, speed limits, road conditions, hazards, or traffic rules.
- If important information is missing, unclear, or ambiguous, state the uncertainty instead of guessing.
- Never infer a speed limit unless it is explicitly provided.

2. TRAFFIC UNDERSTANDING

Focus on the information relevant to the driving decision:

- Road geometry and road structure
- Lane configuration and lane boundaries
- Ego lane and ego-vehicle position
- Vehicle offset within the ego lane
- Relevant neighboring lanes
- Traffic signs and signals
- Explicitly provided traffic rules or speed limits
- Other information only when it directly affects the driving decision

Do not mention information merely because it is available.

3. DECISION MAKING

- Base the recommendation on the actual traffic situation and available evidence.
- Use the most decision-relevant road, lane, ego-position, and traffic-sign evidence to support the recommendation.
- Prefer maintaining the current lane when there is no evidence requiring a change.
- Do not recommend lane changes, overtaking, acceleration, or braking without a clear evidence-based reason.
- If uncertainty affects the decision, choose the safer reasonable action and briefly state the uncertainty.
- Do not give generic driving advice unrelated to the current scene.

4. HALLUCINATION CONTROL

- Never fill missing information with assumptions.
- Missing or undetected information does not prove that the corresponding object does not exist.
- Do not create traffic rules, speed limits, hazards, or road events that are not supported by the evidence.
- Do not silently resolve contradictory evidence by inventing information.

5. OUTPUT

The final response must be concise, practical, and specific.
Do not describe the reasoning process.
Do not mention the input format, model, prompt, or perception pipeline.
Do not repeat the same information across sections.
""",
    "image_only": """
Use the provided traffic scene image as the ONLY source of information.

Base the assessment only on visually observable or reasonably identifiable evidence in the image.

Focus on:

- Road geometry and road structure
- Lane configuration and lane boundaries
- Ego lane and ego-vehicle position
- Vehicle offset when visually identifiable
- Relevant neighboring lanes
- Visible traffic signs and signals
- Visible road markings relevant to the driving decision

Do not infer details that cannot reasonably be determined from the image.

If important information cannot be reliably determined from the image, acknowledge the uncertainty instead of guessing.
   """,
    "json_only": """
Use the provided semantic scene JSON as the ONLY source of information.

The JSON contains structured information extracted from the traffic scene.

Use all relevant information explicitly represented in the JSON, especially:
- Road geometry and road structure
- Lane configuration and lane boundaries
- Ego lane and ego-vehicle position
- Vehicle offset
- Neighboring lanes
- Traffic signs and signals
- Explicitly provided traffic rules or speed limits

Treat the JSON as perception output, not unquestionable ground truth.

Do not infer visual information that is not represented in the JSON.

Do not assume that missing fields or empty detections mean that the corresponding object does not exist.

If the JSON is incomplete, ambiguous, or internally inconsistent, acknowledge the limitation instead of inventing missing information.

Use the semantic information to support the driving recommendation, not merely to describe the scene.
    Json data:
    {json}""",

    "image_json": """
Use BOTH the provided traffic scene image and the semantic scene JSON as complementary sources of evidence.

The image provides direct visual evidence.
The semantic JSON provides structured perception information.

Use information from BOTH sources when relevant.

For each important fact:

- Use the image when it provides clear visual evidence.
- Use the JSON when it provides structured information that is difficult, ambiguous, or impossible to determine reliably from the image.
- Use both sources when they provide consistent evidence.
- Do not ignore information simply because it is available from only one source.

In particular, use the JSON to supplement visual understanding of:
- Lane configuration and lane boundaries
- Ego lane and ego-vehicle position
- Vehicle offset
- Neighboring lanes
- Traffic signs and signals
- Structured road geometry

Use the image to supplement information that is missing, incomplete, or uncertain in the JSON.

If the image and JSON clearly conflict:
- Do not silently choose one source without considering the conflict.
- Use the source with stronger direct evidence for that specific fact.
- If the conflict affects the driving decision, briefly state the uncertainty.
- Do not invent information to reconcile the conflict.
- Do not assume that the JSON is always correct.

Before making the recommendation, combine the relevant evidence from BOTH sources into one understanding of the traffic situation.

Use the most reliable and decision-relevant information from both sources.
Do not mention information merely to demonstrate that both sources were used.
    Json data:
    {json}""",

    # Chỉ dẫn định dạng output - CỐ TÌNH tách riêng, nối vào CUỐI CÙNG (sau
    # DEFAULT_PROMPTS[mode], tức sau cả khối JSON data với json_only/
    # image_json) thay vì để trong "common". Lý do: nếu để trong "common",
    # chỉ dẫn này sẽ nằm TRƯỚC khối JSON, khiến giữa chỉ dẫn và điểm model
    # bắt đầu sinh câu trả lời có xen 1 đoạn JSON dài - LLM thường tuân thủ
    # tốt hơn các chỉ dẫn nằm gần cuối prompt (recency), nên để xa JSON dài
    # có rủi ro model "quên" ràng buộc output khi JSON càng dài.
    "output_format": """

6. OUTPUT FORMAT

Respond in exactly 3 parts, in this order, as plain sentences (no headers, no markdown):
1. Situation: 1-2 sentences on the specific decision-relevant evidence observed.
2. Recommendation: 1 sentence stating the driving action.
3. Safety note: 1 sentence on the most relevant risk, or state that no specific safety concern was identified.

Every part must reference the specific evidence it relies on (for example: the observed signal color, the specific lane/position fact, the specific hazard) instead of generic statements like "no urgent signs" with no supporting detail.
Do not omit any of the 3 parts, even when the answer is simple.
Do not describe the reasoning process.
Do not mention the input format, model, prompt, or perception pipeline.
Do not repeat the same information across parts.
""",
}


def encode_image_base64(image_path: str, max_kb: Optional[int] = None) -> str:
    """
    Đọc ảnh và encode base64 - dùng để nhúng vào message dạng data URI.

    Args:
        max_kb: nếu truyền vào, ảnh sẽ được resize + giảm chất lượng JPEG lặp
                lại tới khi dung lượng base64 <= max_kb KB. NVIDIA NIM cho
                VLM thường giới hạn kích thước ảnh base64-inline khá nhỏ
                (thường dưới ~180KB) - ảnh dashcam gốc gần như chắc chắn vượt
                ngưỡng này, nên nếu không nén trước sẽ bị API từ chối.
    """
    if max_kb is None:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không đọc được ảnh: {image_path}")

    max_bytes = max_kb * 1024
    quality = 90
    scale = 1.0

    while True:
        if scale < 1.0:
            h, w = image.shape[:2]
            resized = cv2.resize(image, (max(1, int(w * scale)), max(1, int(h * scale))))
        else:
            resized = image

        ok, buf = cv2.imencode(".jpg", resized, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise ValueError(f"Không encode được ảnh: {image_path}")

        b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
        if len(b64) <= max_bytes or (quality <= 30 and scale <= 0.3):
            return b64

        # Giảm chất lượng trước, hết dư địa thì giảm kích thước ảnh
        if quality > 30:
            quality -= 15
        else:
            scale -= 0.15


def _guess_mime_type(image_path: str) -> str:
    ext = os.path.splitext(image_path)[1].lstrip(".").lower()
    return "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext or 'jpeg'}"


def build_messages(
    prompt_template: str,
    image_path: Optional[str],
    json_data: Optional[Dict],
    max_image_kb: Optional[int] = None,
) -> List[Dict]:
    """
    Dựng danh sách messages theo chuẩn OpenAI chat-completions.

    - Nếu json_data khác None: nhúng JSON vào prompt (thay {json} nếu có,
      hoặc nối thêm vào cuối).
    - Nếu image_path khác None: content chuyển sang dạng list block
      (text + image_url dạng base64 data URI) - bắt buộc phải theo định dạng
      này để gửi kèm ảnh qua API OpenAI-compatible.
    """
    text = prompt_template
    if json_data is not None:
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        if "{json}" in text:
            text = text.replace("{json}", json_str)
        else:
            text = f"{text}\n\nJSON data:\n```json\n{json_str}\n```"

    if image_path is None:
        return [{"role": "user", "content": text}]

    image_b64 = encode_image_base64(image_path, max_kb=max_image_kb)
    mime_type = "image/jpeg" if max_image_kb is not None else _guess_mime_type(image_path)
    content = [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
    ]
    return [{"role": "user", "content": content}]


def call_llm(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict],
    max_tokens: int,
    temperature: float,
    top_p: float,
    frequency_penalty: float,
    seed: Optional[int],
    timeout: int,
) -> tuple[str, float]:
    """
    Gọi endpoint chat/completions kiểu NVIDIA NIM (OpenAI-compatible).

    Trả về (text trả lời, request_seconds) - request_seconds chỉ tính thời gian
    của đúng lệnh gọi requests.post() (gửi request tới lúc nhận response), KHÔNG
    tính thời gian đọc file JSON, encode/nén ảnh, hay ghi file output - những
    việc đó nằm ở process_one().
    """
    if not api_key:
        raise ValueError(
            "Thiếu NVIDIA API key. Đặt biến môi trường NVIDIA_API_KEY hoặc truyền --api-key."
        )

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "stream": False,
    }
    if seed is not None:
        payload["seed"] = seed

    request_start = time.time()
    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    request_seconds = time.time() - request_start
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"], request_seconds


def find_stems(mode: str, image_dir: Optional[str], json_dir: Optional[str]) -> List[str]:
    """
    Liệt kê danh sách <tên file> (không mở rộng) cần xử lý, tùy theo mode.

    Bỏ qua các file bắt đầu bằng "_" (ví dụ _summary.json) - đây là quy ước
    đặt tên cho file housekeeping/tổng hợp (batch_process.py và chính script
    này đều tạo ra _summary.json trong thư mục output), không phải JSON scene
    của 1 ảnh cụ thể - nếu không lọc, --json-dir trỏ thẳng vào thư mục output
    của batch_process.py sẽ luôn bị cảnh báo "JSON không có ảnh tương ứng"
    một cách vô nghĩa ở mỗi lần chạy.

    BUG ĐÃ SỬA: batch_process.py (sau khi thêm scene_summarizer.py) giờ ghi
    THÊM <tên>_brief.json (bản rút gọn) cạnh <tên>.json (thô) trong cùng thư
    mục output - file này KHÔNG bắt đầu bằng "_" (chỉ có "_brief" ở giữa tên)
    nên lọt qua bộ lọc cũ, bị hiểu nhầm thành 1 "ảnh" riêng tên "<tên>_brief"
    (gấp đôi số lượng thực tế, gửi nhầm JSON rút gọn cho LLM như thể là scene
    thật). Nay lọc thêm mọi tên kết thúc bằng "_brief".
    """
    def _is_scene_json(name: str) -> bool:
        if not name.lower().endswith(".json") or name.startswith("_"):
            return False
        return not os.path.splitext(name)[0].endswith("_brief")

    if mode == "image_only":
        names = os.listdir(image_dir)
        return sorted(os.path.splitext(n)[0] for n in names if n.lower().endswith(IMAGE_EXTENSIONS) and os.path.splitext(n)[0].isdigit())

    if mode == "json_only":
        names = os.listdir(json_dir)
        return sorted(os.path.splitext(n)[0] for n in names if _is_scene_json(n))

    # image_json: chỉ xử lý các tên xuất hiện ở CẢ 2 thư mục
    image_stems = {os.path.splitext(n)[0] for n in os.listdir(image_dir) if n.lower().endswith(IMAGE_EXTENSIONS) and os.path.splitext(n)[0].isdigit()}
    json_stems = {os.path.splitext(n)[0] for n in os.listdir(json_dir) if _is_scene_json(n)}

    missing_json = sorted(image_stems - json_stems)
    missing_image = sorted(json_stems - image_stems)
    if missing_json:
        logger.warning(f"{len(missing_json)} ảnh không có JSON tương ứng, bỏ qua. Ví dụ: {missing_json[:5]}")
    if missing_image:
        logger.warning(f"{len(missing_image)} JSON không có ảnh tương ứng, bỏ qua. Ví dụ: {missing_image[:5]}")

    return sorted(image_stems & json_stems)


def _resolve_image_path(image_dir: str, stem: str) -> str:
    """Tìm đúng file ảnh (cho phép .jpg/.jpeg/.png) ứng với 1 stem."""
    for ext in IMAGE_EXTENSIONS:
        candidate = os.path.join(image_dir, f"{stem}{ext}")
        if os.path.exists(candidate):
            return candidate
    return os.path.join(image_dir, f"{stem}.jpg")  # fallback, sẽ lỗi rõ ràng khi mở file nếu không tồn tại


def process_one(args, stem: str) -> float:
    """Xử lý 1 stem, trả về request_seconds (thời gian riêng của lệnh gọi API - xem call_llm())."""
    image_path = _resolve_image_path(args.image_dir, stem) if args.mode in ("image_only", "image_json") else None

    json_data = None
    if args.mode in ("json_only", "image_json"):
        # Dùng JSON RÚT GỌN (_brief.json) làm input cho VLM, không dùng JSON
        # thô (<stem>.json) nữa - xem lý do ở scene_summarizer.py và mục 3.4
        # luận văn (json_brief nay đã có traffic_signs, đủ cho rubric đánh giá
        # tiêu chí biển báo/quy tắc ở mọi chế độ input). find_stems() vẫn liệt
        # kê stem dựa trên <stem>.json thô (không đổi) để không nhầm _brief.json
        # thành 1 "ảnh" riêng - chỉ đổi FILE THỰC SỰ ĐƯỢC ĐỌC ở đây.
        json_path = os.path.join(args.json_dir, f"{stem}_brief.json")
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

    messages = build_messages(args.prompt_template, image_path, json_data, max_image_kb=args.max_image_kb)
    if args.system:
        messages = [{"role": "system", "content": args.system}] + messages

    answer, request_seconds = call_llm(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        frequency_penalty=args.frequency_penalty,
        seed=args.seed,
        timeout=args.timeout,
    )

    out_path = os.path.join(args.output_dir, f"{stem}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(answer)

    return request_seconds


TIMING_LOG_FILENAME = "_request_timings.json"


def load_timing_log(output_dir: str) -> Dict[str, Dict]:
    """Đọc file log thời gian request đã có (nếu có) trong output_dir."""
    path = os.path.join(output_dir, TIMING_LOG_FILENAME)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_timing_log(output_dir: str, timing_log: Dict[str, Dict]) -> None:
    path = os.path.join(output_dir, TIMING_LOG_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(timing_log, f, indent=2, ensure_ascii=False, sort_keys=True)


def run_batch(args) -> None:
    os.makedirs(args.output_dir, exist_ok=True)

    # File log thời gian request, 1 entry/stem - khi chạy lại đúng stem đó
    # (--overwrite, hoặc output .txt bị xóa), entry cũ bị GHI ĐÈ bằng lần đo
    # mới nhất, không cộng dồn/nhân bản.
    timing_log = load_timing_log(args.output_dir)

    stems = find_stems(args.mode, args.image_dir, args.json_dir)
    if args.stems:
        wanted = [s.strip() for s in args.stems.split(",") if s.strip()]
        missing = [s for s in wanted if s not in stems]
        if missing:
            logger.warning(f"{len(missing)} stem trong --stems không tìm thấy dữ liệu tương ứng, bỏ qua: {missing}")
        stems = [s for s in wanted if s in stems]
    if args.limit:
        stems = stems[: args.limit]
    if not stems:
        logger.error("Không tìm thấy mục nào để xử lý - kiểm tra lại --image-dir/--json-dir.")
        return

    logger.info(f"Chế độ: {args.mode}. Model: {args.model}. Tổng {len(stems)} mục cần xử lý.")

    succeeded = 0
    failures = []
    batch_start = time.time()

    for i, stem in enumerate(stems, start=1):
        out_path = os.path.join(args.output_dir, f"{stem}.txt")
        if os.path.exists(out_path) and not args.overwrite:
            logger.info(f"[{i}/{len(stems)}] Bỏ qua (đã có output): {stem}")
            continue

        start = time.time()
        try:
            request_seconds = process_one(args, stem)
            elapsed = time.time() - start
            succeeded += 1
            logger.info(f"[{i}/{len(stems)}] OK {stem} ({elapsed:.1f}s, API {request_seconds:.1f}s)")

            timing_log[stem] = {
                "request_seconds": round(request_seconds, 3),
                "total_seconds": round(elapsed, 3),
                "mode": args.mode,
                "model": args.model,
                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            save_timing_log(args.output_dir, timing_log)
        except Exception as exc:  # noqa: BLE001 - lỗi 1 mục không được làm dừng cả batch
            logger.error(f"[{i}/{len(stems)}] LỖI {stem}: {exc}")
            failures.append({"stem": stem, "error": str(exc)})

    total_elapsed = time.time() - batch_start
    summary = {
        "mode": args.mode,
        "model": args.model,
        "base_url": args.base_url,
        "total": len(stems),
        "succeeded": succeeded,
        "failed": len(failures),
        "failures": failures,
        "total_elapsed_seconds": round(total_elapsed, 2),
    }
    with open(os.path.join(args.output_dir, "_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"HOÀN TẤT: {succeeded}/{len(stems)} thành công, {len(failures)} lỗi. Chi tiết: _summary.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gọi NVIDIA NIM hàng loạt (ảnh/JSON -> .txt)")
    parser.add_argument("--mode", choices=["image_only", "json_only", "image_json"], required=True)
    parser.add_argument("--image-dir", type=str, default=None, help="Thư mục chứa ảnh <tên>.jpg (bắt buộc với image_only/image_json)")
    parser.add_argument("--json-dir", type=str, default=None, help="Thư mục chứa JSON <tên>.json (bắt buộc với json_only/image_json)")
    parser.add_argument("--output-dir", type=str, required=True, help="Thư mục lưu <tên>.txt")

    parser.add_argument(
        "--prompt", type=str, default=None,
        help="Ghi đè prompt mặc định (DEFAULT_PROMPTS trong file) - thường KHÔNG cần truyền, sửa trực tiếp DEFAULT_PROMPTS khi muốn đổi prompt lâu dài.",
    )
    parser.add_argument("--prompt-file", type=str, default=None, help="Ghi đè prompt bằng nội dung 1 file (thay cho --prompt)")
    parser.add_argument("--system", type=str, default=None, help="System prompt (tùy chọn)")

    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help=f"Mặc định: {DEFAULT_BASE_URL}")
    parser.add_argument("--api-key", type=str, default=os.environ.get("NVIDIA_API_KEY"), help="Mặc định đọc từ biến môi trường NVIDIA_API_KEY")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument(
        "--max-tokens", type=int, default=400,
        help="Giới hạn token sinh ra - hạ từ 1024 xuống 400 (mặc định) để chặn thiệt hại nếu model bị lặp "
             "vô hạn (đã gặp thực tế: 1 output lặp cùng 1 câu ~6 lần rồi bị cắt cụt ở max_tokens cũ).",
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.7)
    parser.add_argument(
        "--frequency-penalty", type=float, default=0.4,
        help="Phạt token lặp lại (0.0-2.0, chuẩn OpenAI-compatible) - thêm để chặn hiện tượng model lặp "
             "vô hạn cùng 1 câu (gặp thực tế ở ảnh có ít thông tin, model lặp lại "
             "'The image does not provide enough information...' nhiều lần liên tiếp).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Cố định seed để kết quả tái lập được (tùy chọn)")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout mỗi request (giây)")
    parser.add_argument(
        "--max-image-kb", type=int, default=150,
        help="Nén/resize ảnh trước khi encode base64 cho tới khi <= giá trị này (KB). "
             "Đặt 0 để tắt (gửi ảnh gốc nguyên vẹn, có thể bị NVIDIA NIM từ chối nếu quá lớn).",
    )

    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số mục xử lý (test nhanh)")
    parser.add_argument(
        "--stems", type=str, default=None,
        help="Chỉ xử lý đúng các tên file này (không phần mở rộng), cách nhau bởi dấu phẩy, "
             "ví dụ --stems 1,9,27,50,116 - dùng để test nhanh 1 bộ ảnh chẩn đoán cố định sau "
             "mỗi lần sửa prompt, thay vì phải chạy hết cả thư mục.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Ghi đè cả những mục đã có sẵn .txt output")

    args = parser.parse_args()
    setup_logging()

    if not args.api_key:
        parser.error("Thiếu NVIDIA API key - đặt biến môi trường NVIDIA_API_KEY hoặc truyền --api-key.")

    # Thứ tự ưu tiên: --prompt > --prompt-file > DEFAULT_PROMPTS[mode] (hardcode trong file)
    if args.prompt:
        args.prompt_template = args.prompt
    elif args.prompt_file:
        args.prompt_template = open(args.prompt_file, "r", encoding="utf-8").read()
    else:
        args.prompt_template = DEFAULT_PROMPTS["common"] + DEFAULT_PROMPTS[args.mode] + DEFAULT_PROMPTS["output_format"]

    if args.mode in ("image_only", "image_json") and not args.image_dir:
        parser.error("--image-dir bắt buộc với mode này")
    if args.mode in ("json_only", "image_json") and not args.json_dir:
        parser.error("--json-dir bắt buộc với mode này")

    args.max_image_kb = args.max_image_kb if args.max_image_kb and args.max_image_kb > 0 else None

    run_batch(args)


if __name__ == "__main__":
    main()
