"""
Chấm điểm output LLM bằng GPT (OpenAI API), dùng ĐÚNG NGUYÊN VĂN prompt/rubric
đang dùng cho Gemini (import trực tiếp EVALUATION_INSTRUCTIONS/EVALUATION_CRITERIA
và hàm dựng prompt _build_evaluation_prompt() từ score_output_by_gemini.py -
KHÔNG chép lại nội dung, để đảm bảo 2 judge chấm cùng 1 đề bài tuyệt đối
giống nhau, không lệch do khác prompt).

Mục đích: so sánh độ đồng thuận của GPT với người, đối chiếu với độ đồng
thuận của Gemini với người (đã đo ở evaluate_human_agreement.py) - xem mục 5
báo cáo tiến độ. Mốc so sánh ĐÚNG là điểm người chấm (human_agreement_sample.xlsx),
KHÔNG phải so trực tiếp điểm GPT với điểm Gemini.

Cần biến môi trường OPENAI_API_KEY trước khi chạy:
    export OPENAI_API_KEY="sk-..."          # bash
    $env:OPENAI_API_KEY = "sk-..."          # PowerShell

Cách dùng (từ thư mục src-v2):
    # Mặc định: chấm đúng 20 ảnh trong human_agreement_sample.xlsx (dùng cho
    # so sánh với người + với Gemini)
    python score_output_by_gpt.py

    # Chỉ định ảnh khác / thư mục khác
    python score_output_by_gpt.py --stems 1,9,27,50,116 --experiment-folder output-suggest-image-json-prompt-v5-31b
"""

import argparse
import base64
import json
import os
import time
from typing import Dict, List, Optional

import pandas as pd
import requests

from score_output_by_gemini import (
    EVALUATION_CRITERIA,
    _accumulate_scores,
    _build_evaluation_prompt,
    _guess_mime_type,
    read_text_file,
)
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_IMAGES_FOLDER = "input"
DEFAULT_EXPERIMENT_FOLDER = "output-suggest-image-json-prompt-v5-31b"
DEFAULT_EXPERIMENT_NAME = "ising_calibration_31b"
DEFAULT_OUTPUT_DIR = "evaluation_results/gpt_judge1"
DEFAULT_STEMS_SOURCE = "human_agreement_sample.xlsx"  # cột "Image" - 20 ảnh đã có điểm người chấm

MAX_RETRIES = 5
RETRY_DELAY_FALLBACK_SECONDS = 20.0


def _default_stems() -> List[str]:
    """Lấy danh sách ảnh mặc định = đúng 20 ảnh đã có điểm người chấm, để so sánh công bằng với Gemini."""
    if not os.path.exists(DEFAULT_STEMS_SOURCE):
        return []
    df = pd.read_excel(DEFAULT_STEMS_SOURCE)
    df.columns = [c.strip() for c in df.columns]
    return [str(int(x)) for x in df["Image"]]


def call_gpt_evaluate(
    image_path: str,
    experiment_outputs: Dict[str, str],
    api_key: str,
    model: str,
) -> Optional[Dict[str, Dict]]:
    """
    Gọi GPT MỘT LẦN để chấm điểm - dùng ĐÚNG prompt do _build_evaluation_prompt()
    dựng ra (nguyên văn EVALUATION_INSTRUCTIONS + cùng cấu trúc output JSON
    yêu cầu như bên Gemini).
    """
    prompt = _build_evaluation_prompt(experiment_outputs)

    try:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
    except OSError as e:
        logger.warning(f"Lỗi đọc ảnh {image_path}: {e}")
        return None

    mime_type = _guess_mime_type(image_path)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
            ],
        }],
        # "temperature": 0.1,
        "max_completion_tokens": 4096,
        # Ép trả JSON thuần, tương đương response_mime_type="application/json" bên Gemini.
        "response_format": {"type": "json_object"},
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 429 or response.status_code >= 500:
                raise requests.HTTPError(f"{response.status_code}: {response.text[:300]}", response=response)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except json.JSONDecodeError as e:
            if attempt >= MAX_RETRIES:
                logger.error(f"Hết {MAX_RETRIES} lần thử do GPT liên tục trả JSON sai cú pháp: {e}")
                return None
            logger.warning(f"[Thử lại {attempt}/{MAX_RETRIES}] Response không phải JSON hợp lệ, thử lại sau 3s")
            time.sleep(3.0)
        except requests.HTTPError as e:
            if e.response is not None:
                try:
                    error_body = e.response.json()
                except Exception:
                    error_body = e.response.text

                logger.error(
                    f"OpenAI API error "
                    f"status={e.response.status_code}: {error_body}"
                )

            if attempt >= MAX_RETRIES:
                logger.error(
                    f"Hết {MAX_RETRIES} lần thử do lỗi HTTP: {e}"
                )
                return None

            time.sleep(RETRY_DELAY_FALLBACK_SECONDS)
        except Exception as e:  # noqa: BLE001 - lỗi 1 ảnh không được làm dừng cả batch
            logger.error(f"Lỗi gọi GPT ({type(e).__name__}): {e}")
            return None

    return None


def evaluate_stems(
    images_folder: str,
    experiment_folder: str,
    experiment_name: str,
    stems: List[str],
    output_dir: str,
    api_key: str,
    model: str,
    delay: float = 2.0,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    scores_accumulator: Dict[str, list] = {key: [] for key in EVALUATION_CRITERIA}
    evaluated = 0

    for i, stem in enumerate(stems, start=1):
        image_path = None
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = os.path.join(images_folder, f"{stem}{ext}")
            if os.path.exists(candidate):
                image_path = candidate
                break
        if image_path is None:
            logger.warning(f"[{i}/{len(stems)}] Không tìm thấy ảnh cho stem={stem}, bỏ qua")
            continue

        txt_path = os.path.join(experiment_folder, f"{stem}.txt")
        content = read_text_file(txt_path)
        if not content:
            logger.warning(f"[{i}/{len(stems)}] Không tìm thấy output tại {txt_path}, bỏ qua")
            continue

        out_path = os.path.join(output_dir, f"{stem}.json")
        logger.info(f"[{i}/{len(stems)}] Đang chấm điểm: {stem}")
        result = call_gpt_evaluate(image_path, {experiment_name: content}, api_key, model)

        if result and experiment_name in result and "scores" in result[experiment_name]:
            result[experiment_name]["image"] = os.path.basename(image_path)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            _accumulate_scores(result[experiment_name], scores_accumulator)
            evaluated += 1
            logger.info(f"  -> Đã lưu {out_path}")
        else:
            logger.error(f"  Lỗi khi chấm điểm ảnh {stem}")

        if i < len(stems):
            time.sleep(delay)

    logger.info(f"HOÀN TẤT: {evaluated}/{len(stems)} ảnh chấm được. Kết quả tại: {output_dir}")
    if evaluated > 0:
        logger.info("Điểm trung bình theo tiêu chí:")
        for key, values in scores_accumulator.items():
            if values:
                logger.info(f"  {key}: {sum(values) / len(values):.2f} (n={len(values)})")


def evaluate_all_experiments(
    images_folder: str,
    experiment_folders: Dict[str, str],
    output_dir: str,
    api_key: str,
    model: str,
    overwrite_existing: bool = False,
    delay: float = 2.0,
) -> None:
    """
    Chấm điểm NHIỀU thí nghiệm (ví dụ 3 mode ảnh/JSON/ảnh+JSON) cùng lúc,
    MỖI ẢNH 1 REQUEST DUY NHẤT (gộp cả N thí nghiệm vào 1 prompt qua
    _build_evaluation_prompt) - giống hệt kiến trúc evaluate_all_experiments()
    bên score_output_by_gemini.py, để tiết kiệm chi phí GPT (N ảnh thay vì
    N x số thí nghiệm request).
    """
    os.makedirs(output_dir, exist_ok=True)

    valid_folders = {name: folder for name, folder in experiment_folders.items() if os.path.isdir(folder)}
    missing = set(experiment_folders) - set(valid_folders)
    if missing:
        logger.warning(f"Bỏ qua thí nghiệm không có thư mục: {missing}")
    if not valid_folders:
        logger.error("Không có thư mục thí nghiệm nào hợp lệ.")
        return

    image_files = sorted(f for f in os.listdir(images_folder) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    logger.info(f"Tổng {len(image_files)} ảnh, {len(valid_folders)} thí nghiệm: {list(valid_folders)}")

    exp_scores: Dict[str, Dict[str, list]] = {exp: {key: [] for key in EVALUATION_CRITERIA} for exp in valid_folders}
    exp_evaluated_count: Dict[str, int] = {exp: 0 for exp in valid_folders}

    for i, image_file in enumerate(image_files, start=1):
        base_name = os.path.splitext(image_file)[0]
        combined_path = os.path.join(output_dir, f"{base_name}.json")

        if os.path.exists(combined_path) and not overwrite_existing:
            try:
                cached = json.loads(read_text_file(combined_path) or "{}")
            except json.JSONDecodeError:
                cached = None
            if cached is not None and all(exp in cached for exp in valid_folders):
                logger.info(f"[{i}/{len(image_files)}] Bỏ qua (đã có sẵn): {base_name}")
                for exp_name in valid_folders:
                    _accumulate_scores(cached[exp_name], exp_scores[exp_name])
                    exp_evaluated_count[exp_name] += 1
                continue

        experiment_outputs: Dict[str, str] = {}
        missing_out = []
        for exp_name, exp_folder in valid_folders.items():
            content = read_text_file(os.path.join(exp_folder, f"{base_name}.txt"))
            if content:
                experiment_outputs[exp_name] = content
            else:
                missing_out.append(exp_name)
        if missing_out:
            logger.warning(f"[{i}/{len(image_files)}] Thiếu output ở {missing_out}, bỏ qua ảnh {base_name}")
            continue

        image_path = os.path.join(images_folder, image_file)
        logger.info(f"[{i}/{len(image_files)}] Đang chấm điểm ({len(experiment_outputs)} thí nghiệm cùng lúc): {base_name}")
        result = call_gpt_evaluate(image_path, experiment_outputs, api_key, model)

        if result and all(exp in result and "scores" in result[exp] for exp in experiment_outputs):
            for exp_name in experiment_outputs:
                result[exp_name]["image"] = image_file
            with open(combined_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            for exp_name in experiment_outputs:
                _accumulate_scores(result[exp_name], exp_scores[exp_name])
                exp_evaluated_count[exp_name] += 1
            logger.info(f"  -> Đã lưu {combined_path}")
        else:
            logger.error(f"  Lỗi khi chấm điểm ảnh {base_name}")

        if i < len(image_files):
            time.sleep(delay)

    logger.info("=" * 70)
    logger.info("KẾT QUẢ TỔNG HỢP (GPT)")
    logger.info("=" * 70)
    for exp_name in valid_folders:
        avg = {k: (sum(v) / len(v) if v else 0.0) for k, v in exp_scores[exp_name].items()}
        logger.info(f"{exp_name}: {exp_evaluated_count[exp_name]} ảnh")
        for k, v in avg.items():
            logger.info(f"  - {k}: {v:.2f}")

    final_summary = {
        "total_experiments": len(valid_folders),
        "experiment_results": {
            exp: {
                "total_evaluated": exp_evaluated_count[exp],
                "average_scores": {k: (sum(v) / len(v) if v else 0.0) for k, v in exp_scores[exp].items()},
            }
            for exp in valid_folders
        },
    }
    with open(os.path.join(output_dir, "_final_summary.json"), "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2, ensure_ascii=False)
    logger.info(f"Hoàn thành! Kết quả tại: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chấm điểm output LLM bằng GPT, dùng đúng prompt của Gemini")
    parser.add_argument("--images-folder", type=str, default=DEFAULT_IMAGES_FOLDER)
    parser.add_argument("--experiment-folder", type=str, default=DEFAULT_EXPERIMENT_FOLDER)
    parser.add_argument("--experiment-name", type=str, default=DEFAULT_EXPERIMENT_NAME)
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--api-key", type=str, default=os.environ.get("OPENAI_API_KEY"))
    parser.add_argument(
        "--stems", type=str, default=None,
        help="Danh sách ảnh cần chấm, cách nhau dấu phẩy. Mặc định: 20 ảnh trong human_agreement_sample.xlsx.",
    )
    parser.add_argument("--delay", type=float, default=2.0, help="Thời gian chờ giữa các request (giây)")
    args = parser.parse_args()

    setup_logging()

    if not args.api_key:
        parser.error("Thiếu OpenAI API key - đặt biến môi trường OPENAI_API_KEY hoặc truyền --api-key.")

    stems = [s.strip() for s in args.stems.split(",")] if args.stems else _default_stems()
    if not stems:
        logger.error(f"Không có ảnh nào để chấm - kiểm tra {DEFAULT_STEMS_SOURCE} hoặc truyền --stems.")
        return

    logger.info(f"Model: {args.model}. Tổng {len(stems)} ảnh cần chấm.")
    evaluate_stems(
        images_folder=args.images_folder,
        experiment_folder=args.experiment_folder,
        experiment_name=args.experiment_name,
        stems=stems,
        output_dir=args.output_dir,
        api_key=args.api_key,
        model=args.model,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
