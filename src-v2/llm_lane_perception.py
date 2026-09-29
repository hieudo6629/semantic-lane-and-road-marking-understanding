"""
Kiểm chứng: model VLM có tự phát hiện được ngữ nghĩa làn đường từ ẢNH THÔ
chính xác tới đâu, so với tầng UFLD-v2 + xử lý ngữ nghĩa hiện tại (output-v4/
<tên>_brief.json)?

Gửi CHỈ ảnh (không kèm JSON nào) cho model VLM qua NVIDIA NIM, yêu cầu trả
về JSON đúng schema của <tên>_brief.json hiện tại (xem
analysis/scene_summarizer.py, đã bổ sung "order" và "traffic_signs"):
    lane_count, order,
    ego_lane{position, confidence},
    vehicle_offset{direction, magnitude, offset_percent},
    neighbor_lanes{left_count, right_count},
    road_shape{type, severity, direction},
    traffic_signs{detected[{sign_type, relative_position, distance}], count}

Output mỗi ảnh lưu 1 file <tên>_llm_brief.json (nếu parse JSON thành công)
hoặc <tên>_llm_brief.txt (nếu model trả về không phải JSON hợp lệ - vẫn lưu
lại để không mất dữ liệu, xem log cảnh báo).

Tái sử dụng encode_image_base64/_guess_mime_type/call_llm từ
llm_batch_client.py (không viết lại logic gọi API).

Cần biến môi trường NVIDIA_API_KEY (hoặc truyền --api-key) trước khi chạy:
    export NVIDIA_API_KEY="nvapi-..."          # bash
    $env:NVIDIA_API_KEY = "nvapi-..."           # PowerShell

Cách dùng (từ thư mục src-v2):
    python llm_lane_perception.py --input-dir input --output-dir output-llm-lane-perception
    python llm_lane_perception.py --input-dir input --output-dir output-llm-lane-perception --stems 1,9,27 --overwrite
"""

import argparse
import json
import os
import re
import time
from typing import Optional

from llm_batch_client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    IMAGE_EXTENSIONS,
    call_llm,
    encode_image_base64,
    _guess_mime_type,
)
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# Prompt CỐ TÌNH không nhắc gì tới UFLD-v2/JSON có sẵn - mục đích là đo khả
# năng của VLM khi phải tự cảm nhận làn đường từ ảnh, không được "gà bài".
PROMPT = """
You are a lane-level visual perception assistant. Your ONLY task is to visually
analyze the provided traffic scene image and output structured lane-level
information as JSON. Do NOT provide any driving recommendation, explanation,
or commentary - ONLY the JSON object described below.

Determine the following fields, based ONLY on what is visually observable in
the image (do not invent lanes, boundaries, or road structure that are not
clearly visible):

1. lane_count (integer)
   - Number of relevant drivable lanes in the ego vehicle's direction of
     travel that are visible in the image. Count actual LANES, not lane
     boundary lines (number of lanes = number of boundaries - 1).

2. ego_lane
   - position (string): position of the ego lane counting from the LEFT,
     in the form "X/Y" where X = ego lane index (1 = leftmost lane) and
     Y = lane_count. Use "unknown" if this cannot be reliably determined.
   - confidence (float, 0.0-1.0): your confidence in this ego lane position.

3. vehicle_offset
   - direction (string): one of "left", "right", "centered", "unknown" -
     direction of the ego vehicle's lateral offset from the lane center.
   - magnitude (string): one of "none", "slight", "significant", "unknown".
   - offset_percent (number or null): estimated lateral offset as a
     percentage of lane width (0 = perfectly centered), or null if this
     cannot be reasonably estimated from the image.

4. neighbor_lanes
   - left_count (integer): number of lanes to the LEFT of the ego lane,
     going the same direction of travel.
   - right_count (integer): number of lanes to the RIGHT of the ego lane,
     going the same direction of travel.

5. road_shape
   - type (string): one of "straight", "curve", "unknown".
   - severity (string): "none" if type is "straight", otherwise one of
     "gentle", "sharp", "unknown".
   - direction (string or null): "left" or "right" if type is "curve",
     otherwise null.

6. order (string)
   - Always the fixed string "left to right" - lane_count, ego_lane.position,
     and neighbor_lanes above are all counted/ordered from left to right as
     seen in the image. Just copy this fixed value, it is not something to
     visually detect.

7. traffic_signs
   - detected (array): one entry per traffic sign or traffic light clearly
     visible in the image (empty array if none). Each entry:
       - sign_type (string): a short plain-language description of the sign
         (e.g. "speed limit 60", "no entry", "pedestrian crossing warning",
         "red traffic light"). Do not invent signs that are not visible.
       - relative_position (string): one of "left", "center", "right".
       - distance (string): one of "near", "medium", "far".
   - count (integer): total number of entries in the detected list above.

If a field cannot be reliably determined from the image, use "unknown" (or
null where the field allows it) instead of guessing.

OUTPUT FORMAT - respond with ONLY a single valid JSON object, no markdown
code fences, no explanation, no extra text, in EXACTLY this structure:
{
  "lane_count": <int>,
  "ego_lane": {"position": "<string>", "confidence": <float>},
  "vehicle_offset": {"direction": "<string>", "magnitude": "<string>", "offset_percent": <number or null>},
  "neighbor_lanes": {"left_count": <int>, "right_count": <int>},
  "road_shape": {"type": "<string>", "severity": "<string>", "direction": "<string or null>"},
  "order": "left to right",
  "traffic_signs": {"detected": [{"sign_type": "<string>", "relative_position": "<string>", "distance": "<string>"}], "count": <int>}
}
"""

REQUIRED_KEYS = ("lane_count", "ego_lane", "vehicle_offset", "neighbor_lanes", "road_shape", "order", "traffic_signs")


def _extract_json(raw_text: str) -> Optional[dict]:
    """
    Tách JSON từ output model - model đôi khi vẫn bọc trong ```json ... ```
    dù đã được yêu cầu không làm vậy. Trả về None nếu không parse được hoặc
    thiếu key bắt buộc.
    """
    text = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict) or not all(k in data for k in REQUIRED_KEYS):
        return None
    return data


def process_one(args, stem: str, image_path: str) -> None:
    image_b64 = encode_image_base64(image_path, max_kb=args.max_image_kb)
    mime_type = "image/jpeg" if args.max_image_kb is not None else _guess_mime_type(image_path)
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
        ],
    }]

    answer = call_llm(
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

    parsed = _extract_json(answer)
    if parsed is not None:
        out_path = os.path.join(args.output_dir, f"{stem}_llm_brief.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
    else:
        out_path = os.path.join(args.output_dir, f"{stem}_llm_brief.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(answer)
        logger.warning(f"  {stem}: model không trả về JSON hợp lệ đúng schema - đã lưu raw text vào {out_path}")


def run_batch(args) -> None:
    os.makedirs(args.output_dir, exist_ok=True)

    stems = sorted(
        os.path.splitext(n)[0]
        for n in os.listdir(args.input_dir)
        if n.lower().endswith(IMAGE_EXTENSIONS)
        # Chỉ nhận ảnh tên <số>.jpg (bộ N=200 đánh giá) - loại các ảnh khác
        # như "1_observed.jpg" (crop thử nghiệm đo tỉ lệ rho, xem mục 3.3
        # luận văn) để không lẫn vào kết quả tự nhận diện của VLM.
        and os.path.splitext(n)[0].isdigit()
    )
    if args.stems:
        wanted = [s.strip() for s in args.stems.split(",") if s.strip()]
        missing = [s for s in wanted if s not in stems]
        if missing:
            logger.warning(f"{len(missing)} stem không tìm thấy ảnh tương ứng, bỏ qua: {missing}")
        stems = [s for s in wanted if s in stems]
    if args.limit:
        stems = stems[: args.limit]
    if not stems:
        logger.error("Không tìm thấy ảnh nào để xử lý - kiểm tra lại --input-dir.")
        return

    logger.info(f"Model: {args.model}. Tổng {len(stems)} ảnh cần xử lý.")

    succeeded = 0
    failures = []
    batch_start = time.time()

    for i, stem in enumerate(stems, start=1):
        json_out = os.path.join(args.output_dir, f"{stem}_llm_brief.json")
        txt_out = os.path.join(args.output_dir, f"{stem}_llm_brief.txt")
        if not args.overwrite and (os.path.exists(json_out) or os.path.exists(txt_out)):
            logger.info(f"[{i}/{len(stems)}] Bỏ qua (đã có output): {stem}")
            continue

        image_path = None
        for ext in IMAGE_EXTENSIONS:
            candidate = os.path.join(args.input_dir, f"{stem}{ext}")
            if os.path.exists(candidate):
                image_path = candidate
                break

        start = time.time()
        try:
            process_one(args, stem, image_path)
            elapsed = time.time() - start
            succeeded += 1
            logger.info(f"[{i}/{len(stems)}] OK {stem} ({elapsed:.1f}s)")
        except Exception as exc:  # noqa: BLE001 - lỗi 1 ảnh không được làm dừng cả batch
            logger.error(f"[{i}/{len(stems)}] LỖI {stem}: {exc}")
            failures.append({"stem": stem, "error": str(exc)})

        if i < len(stems):
            time.sleep(args.delay)

    total_elapsed = time.time() - batch_start
    summary = {
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
    parser = argparse.ArgumentParser(
        description="Gửi ảnh cho VLM (NVIDIA NIM), yêu cầu tự phát hiện ngữ nghĩa làn đường theo schema _brief.json"
    )
    parser.add_argument("--input-dir", type=str, required=True, help="Thư mục chứa ảnh <tên>.jpg")
    parser.add_argument("--output-dir", type=str, required=True, help="Thư mục lưu <tên>_llm_brief.json/.txt")

    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help=f"Mặc định: {DEFAULT_BASE_URL}")
    parser.add_argument("--api-key", type=str, default=os.environ.get("NVIDIA_API_KEY"), help="Mặc định đọc từ biến môi trường NVIDIA_API_KEY")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=500, help="Output là JSON ngắn gọn nên không cần nhiều token (nâng từ 300 lên 500 sau khi thêm trường traffic_signs, có thể chứa nhiều phần tử)")
    parser.add_argument("--temperature", type=float, default=0.1, help="Thấp hơn mặc định của llm_batch_client vì đây là tác vụ nhận diện, cần tính nhất quán cao, không cần sáng tạo văn phong")
    parser.add_argument("--top-p", type=float, default=0.7)
    parser.add_argument("--frequency-penalty", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=None, help="Cố định seed để kết quả tái lập được (tùy chọn)")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout mỗi request (giây)")
    parser.add_argument(
        "--max-image-kb", type=int, default=150,
        help="Nén/resize ảnh trước khi encode base64 cho tới khi <= giá trị này (KB). Đặt 0 để tắt.",
    )
    parser.add_argument("--delay", type=float, default=1.0, help="Thời gian chờ giữa các request (giây)")

    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số ảnh xử lý (test nhanh)")
    parser.add_argument(
        "--stems", type=str, default=None,
        help="Chỉ xử lý đúng các tên ảnh này (không phần mở rộng), cách nhau bởi dấu phẩy, ví dụ --stems 1,9,27",
    )
    parser.add_argument("--overwrite", action="store_true", help="Ghi đè cả những ảnh đã có sẵn output")

    args = parser.parse_args()
    setup_logging()

    if not args.api_key:
        parser.error("Thiếu NVIDIA API key - đặt biến môi trường NVIDIA_API_KEY hoặc truyền --api-key.")

    args.max_image_kb = args.max_image_kb if args.max_image_kb and args.max_image_kb > 0 else None

    run_batch(args)


if __name__ == "__main__":
    main()
