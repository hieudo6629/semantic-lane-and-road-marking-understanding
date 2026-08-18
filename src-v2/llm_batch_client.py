"""
Gọi LLM hàng loạt qua NVIDIA NIM (integrate.api.nvidia.com, model
nvidia/llama-3.1-nemotron-nano-vl-8b-v1) để lấy response cho từng cặp
ảnh/JSON, lưu kết quả ra file .txt.

Hỗ trợ 3 chế độ (chọn bằng --mode):
    image_only  : chỉ gửi ẢNH + prompt (không kèm JSON)
    json_only   : chỉ gửi prompt có NHÚNG JSON (không kèm ảnh)
    image_json  : gửi cả ẢNH và prompt có NHÚNG JSON

Ảnh (<tên>.jpg) và JSON (<tên>.json) nằm ở 2 thư mục riêng, khớp nhau theo
tên file (không phần mở rộng). Output lưu vào thư mục thứ 3, mỗi mục 1 file
<tên>.txt (+ 1 file _summary.json tổng hợp toàn batch).

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
from typing import Dict, List, Optional

import cv2
import requests

from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# API NVIDIA NIM trực tiếp - KHÔNG qua fcc-server. Model không có tiền tố
# "nvidia_nim/" (tiền tố đó chỉ dùng khi route qua 1 gateway kiểu LiteLLM,
# gọi thẳng NVIDIA thì dùng đúng model id của họ).
DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-nano-vl-8b-v1"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Prompt mặc định cho từng --mode - SỬA TRỰC TIẾP TẠI ĐÂY khi cần đổi nội
# dung (prompt khá dài nên hardcode thay vì phải truyền --prompt mỗi lần
# chạy). Vẫn có thể ghi đè tạm thời bằng --prompt/--prompt-file nếu chỉ
# muốn thử nhanh 1 prompt khác mà không sửa file.
DEFAULT_PROMPTS = {
    "image_only": """
    You are a traffic scene understanding and driving recommendation assistant.
    Your task is to understand the current traffic situation from the information provided and give a safe, objective, evidence-based driving recommendation.
    Follow these rules strictly:
    1. EVIDENCE
    - Use ONLY information supported by the provided input.
    - Do not invent or assume objects, vehicles, lanes, road markings, traffic signs, traffic signals, speed limits, road conditions, hazards, or traffic rules.
    - If important information is unclear, missing, or ambiguous, explicitly state the uncertainty rather than guessing.
    - Never estimate or infer a speed limit when it is not explicitly provided.
    2. TRAFFIC UNDERSTANDING
    Before making a recommendation, consider the following information when available:
    - Road environment and road geometry
    - Ego vehicle position and ego lane
    - Left and right lane boundaries
    - Neighboring lanes
    - Vehicle position relative to the ego lane center
    - Relevant surrounding vehicles and potential conflicts
    - Traffic signs and traffic signals
    - Applicable speed limits or traffic rules explicitly provided
    - Potential hazards and uncertainties
    These are internal considerations. Do not list them unless they are relevant to the final decision.
    3. DECISION MAKING
    - Base the recommendation on the actual traffic situation, not on generic driving advice.
    - Prioritize safety.
    - Do not recommend a lane change unless there is a clear reason supported by the evidence.
    - Do not recommend overtaking unless clearly justified by the available evidence.
    - Do not recommend acceleration or braking unless supported by the traffic situation.
    - If maintaining the current lane and speed is the safest reasonable action, say so explicitly.
    - When uncertainty could affect the driving decision, choose the safer reasonable action and briefly state the uncertainty.
    4. HALLUCINATION CONTROL
    - Never fill missing information with assumptions.
    - Do not treat an absence of detected information as proof that the object does not exist unless the input explicitly supports that conclusion.
    - Do not create traffic rules, speed limits, hazards, or road events that are not supported by the input.
    5. RESPONSE
    - Be concise, practical, and specific.
    - Keep the entire response under 120 words.
    - Focus only on information relevant to the current driving decision.
    - Do not repeat the same information across sections.
    - Do not enumerate hypothetical actions or situations that are not relevant to the current scene.
    - Do not mention the input format, model, prompt, or perception pipeline.
    - Do not describe your reasoning process.
    Respond using exactly this structure:
    ### Situation Assessment
    Maximum 2 sentences.
    ### Driving Recommendation
    Maximum 2 sentences.
    ### Safety Considerations
    - Maximum 3 bullet points.
    - Include only safety considerations relevant to the current scene.
    - Avoid generic advice.
    Use the provided traffic scene image as the only source of information.
    Base your assessment on visually observable evidence in the image.
    Do not infer details that cannot reasonably be determined from the image.
    """,

    "json_only": """
    You are a traffic scene understanding and driving recommendation assistant.
    Your task is to understand the current traffic situation from the information provided and give a safe, objective, evidence-based driving recommendation.
    Follow these rules strictly:
    1. EVIDENCE
    - Use ONLY information supported by the provided input.
    - Do not invent or assume objects, vehicles, lanes, road markings, traffic signs, traffic signals, speed limits, road conditions, hazards, or traffic rules.
    - If important information is unclear, missing, or ambiguous, explicitly state the uncertainty rather than guessing.
    - Never estimate or infer a speed limit when it is not explicitly provided.
    2. TRAFFIC UNDERSTANDING
    Before making a recommendation, consider the following information when available:
    - Road environment and road geometry
    - Ego vehicle position and ego lane
    - Left and right lane boundaries
    - Neighboring lanes
    - Vehicle position relative to the ego lane center
    - Relevant surrounding vehicles and potential conflicts
    - Traffic signs and traffic signals
    - Applicable speed limits or traffic rules explicitly provided
    - Potential hazards and uncertainties
    These are internal considerations. Do not list them unless they are relevant to the final decision.
    3. DECISION MAKING
    - Base the recommendation on the actual traffic situation, not on generic driving advice.
    - Prioritize safety.
    - Do not recommend a lane change unless there is a clear reason supported by the evidence.
    - Do not recommend overtaking unless clearly justified by the available evidence.
    - Do not recommend acceleration or braking unless supported by the traffic situation.
    - If maintaining the current lane and speed is the safest reasonable action, say so explicitly.
    - When uncertainty could affect the driving decision, choose the safer reasonable action and briefly state the uncertainty.
    4. HALLUCINATION CONTROL
    - Never fill missing information with assumptions.
    - Do not treat an absence of detected information as proof that the object does not exist unless the input explicitly supports that conclusion.
    - Do not create traffic rules, speed limits, hazards, or road events that are not supported by the input.
    5. RESPONSE
    - Be concise, practical, and specific.
    - Keep the entire response under 120 words.
    - Focus only on information relevant to the current driving decision.
    - Do not repeat the same information across sections.
    - Do not enumerate hypothetical actions or situations that are not relevant to the current scene.
    - Do not mention the input format, model, prompt, or perception pipeline.
    - Do not describe your reasoning process.
    Respond using exactly this structure:
    ### Situation Assessment
    Maximum 2 sentences.
    ### Driving Recommendation
    Maximum 2 sentences.
    ### Safety Considerations
    - Maximum 3 bullet points.
    - Include only safety considerations relevant to the current scene.
    - Avoid generic advice.
    Use the provided semantic scene JSON as the only source of information.
    The JSON was generated automatically by an upstream perception system.
    Use only information explicitly represented in the JSON.
    Do not infer visual information that is not represented in the JSON.
    Treat the semantic JSON as automatically generated perception data, not as unquestionable ground truth.
    If the JSON is incomplete, ambiguous, or internally inconsistent, acknowledge the limitation rather than inventing missing information.
    Do not describe every field in the JSON. Use only information relevant to the current driving decision.
    Json data:
    {json}""",

    "image_json": """
You are a traffic scene understanding and driving recommendation assistant.
    Your task is to understand the current traffic situation from the information provided and give a safe, objective, evidence-based driving recommendation.
    Follow these rules strictly:
    1. EVIDENCE
    - Use ONLY information supported by the provided input.
    - Do not invent or assume objects, vehicles, lanes, road markings, traffic signs, traffic signals, speed limits, road conditions, hazards, or traffic rules.
    - If important information is unclear, missing, or ambiguous, explicitly state the uncertainty rather than guessing.
    - Never estimate or infer a speed limit when it is not explicitly provided.
    2. TRAFFIC UNDERSTANDING
    Before making a recommendation, consider the following information when available:
    - Road environment and road geometry
    - Ego vehicle position and ego lane
    - Left and right lane boundaries
    - Neighboring lanes
    - Vehicle position relative to the ego lane center
    - Relevant surrounding vehicles and potential conflicts
    - Traffic signs and traffic signals
    - Applicable speed limits or traffic rules explicitly provided
    - Potential hazards and uncertainties
    These are internal considerations. Do not list them unless they are relevant to the final decision.
    3. DECISION MAKING
    - Base the recommendation on the actual traffic situation, not on generic driving advice.
    - Prioritize safety.
    - Do not recommend a lane change unless there is a clear reason supported by the evidence.
    - Do not recommend overtaking unless clearly justified by the available evidence.
    - Do not recommend acceleration or braking unless supported by the traffic situation.
    - If maintaining the current lane and speed is the safest reasonable action, say so explicitly.
    - When uncertainty could affect the driving decision, choose the safer reasonable action and briefly state the uncertainty.
    4. HALLUCINATION CONTROL
    - Never fill missing information with assumptions.
    - Do not treat an absence of detected information as proof that the object does not exist unless the input explicitly supports that conclusion.
    - Do not create traffic rules, speed limits, hazards, or road events that are not supported by the input.
    5. RESPONSE
    - Be concise, practical, and specific.
    - Keep the entire response under 120 words.
    - Focus only on information relevant to the current driving decision.
    - Do not repeat the same information across sections.
    - Do not enumerate hypothetical actions or situations that are not relevant to the current scene.
    - Do not mention the input format, model, prompt, or perception pipeline.
    - Do not describe your reasoning process.
    Respond using exactly this structure:
    ### Situation Assessment
    Maximum 2 sentences.
    ### Driving Recommendation
    Maximum 2 sentences.
    ### Safety Considerations
    - Maximum 3 bullet points.
    - Include only safety considerations relevant to the current scene.
    - Avoid generic advice.
    Use BOTH the provided traffic scene image and the semantic scene JSON.
    The image provides direct visual evidence about the traffic scene.
    The semantic JSON provides structured perception information extracted from the scene.
    Use both sources together to build the most accurate understanding of the current traffic situation.
    - When the image and JSON agree, combine their information.
    - When the JSON provides useful structured information that is not directly measurable from the image, use it as supporting information.
    - When the image provides clear visual evidence that is missing or inconsistent with the JSON, use the visual evidence for the traffic assessment.
    - When the two sources clearly conflict and the conflict affects the driving decision, briefly state the uncertainty.
    - Do not silently modify, reinterpret, or invent information to reconcile conflicts.
    - Do not assume that the JSON is always correct.
    - Do not describe every field in the JSON. Use only information relevant to the current driving decision.
    Json data:
    {json}""",
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
    seed: Optional[int],
    timeout: int,
) -> str:
    """Gọi endpoint chat/completions kiểu NVIDIA NIM (OpenAI-compatible), trả về text trả lời."""
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
        "stream": False,
    }
    if seed is not None:
        payload["seed"] = seed

    response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def find_stems(mode: str, image_dir: Optional[str], json_dir: Optional[str]) -> List[str]:
    """
    Liệt kê danh sách <tên file> (không mở rộng) cần xử lý, tùy theo mode.

    Bỏ qua các file bắt đầu bằng "_" (ví dụ _summary.json) - đây là quy ước
    đặt tên cho file housekeeping/tổng hợp (batch_process.py và chính script
    này đều tạo ra _summary.json trong thư mục output), không phải JSON scene
    của 1 ảnh cụ thể - nếu không lọc, --json-dir trỏ thẳng vào thư mục output
    của batch_process.py sẽ luôn bị cảnh báo "JSON không có ảnh tương ứng"
    một cách vô nghĩa ở mỗi lần chạy.
    """
    if mode == "image_only":
        names = os.listdir(image_dir)
        return sorted(os.path.splitext(n)[0] for n in names if n.lower().endswith(IMAGE_EXTENSIONS) and not n.startswith("_"))

    if mode == "json_only":
        names = os.listdir(json_dir)
        return sorted(os.path.splitext(n)[0] for n in names if n.lower().endswith(".json") and not n.startswith("_"))

    # image_json: chỉ xử lý các tên xuất hiện ở CẢ 2 thư mục
    image_stems = {os.path.splitext(n)[0] for n in os.listdir(image_dir) if n.lower().endswith(IMAGE_EXTENSIONS) and not n.startswith("_")}
    json_stems = {os.path.splitext(n)[0] for n in os.listdir(json_dir) if n.lower().endswith(".json") and not n.startswith("_")}

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


def process_one(args, stem: str) -> None:
    image_path = _resolve_image_path(args.image_dir, stem) if args.mode in ("image_only", "image_json") else None

    json_data = None
    if args.mode in ("json_only", "image_json"):
        json_path = os.path.join(args.json_dir, f"{stem}.json")
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

    messages = build_messages(args.prompt_template, image_path, json_data, max_image_kb=args.max_image_kb)
    if args.system:
        messages = [{"role": "system", "content": args.system}] + messages

    answer = call_llm(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        messages=messages,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        seed=args.seed,
        timeout=args.timeout,
    )

    out_path = os.path.join(args.output_dir, f"{stem}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(answer)


def run_batch(args) -> None:
    os.makedirs(args.output_dir, exist_ok=True)

    stems = find_stems(args.mode, args.image_dir, args.json_dir)
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
            process_one(args, stem)
            elapsed = time.time() - start
            succeeded += 1
            logger.info(f"[{i}/{len(stems)}] OK {stem} ({elapsed:.1f}s)")
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
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=None, help="Cố định seed để kết quả tái lập được (tùy chọn)")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout mỗi request (giây)")
    parser.add_argument(
        "--max-image-kb", type=int, default=150,
        help="Nén/resize ảnh trước khi encode base64 cho tới khi <= giá trị này (KB). "
             "Đặt 0 để tắt (gửi ảnh gốc nguyên vẹn, có thể bị NVIDIA NIM từ chối nếu quá lớn).",
    )

    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số mục xử lý (test nhanh)")
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
        args.prompt_template = DEFAULT_PROMPTS[args.mode]

    if args.mode in ("image_only", "image_json") and not args.image_dir:
        parser.error("--image-dir bắt buộc với mode này")
    if args.mode in ("json_only", "image_json") and not args.json_dir:
        parser.error("--json-dir bắt buộc với mode này")

    args.max_image_kb = args.max_image_kb if args.max_image_kb and args.max_image_kb > 0 else None

    run_batch(args)


if __name__ == "__main__":
    main()
