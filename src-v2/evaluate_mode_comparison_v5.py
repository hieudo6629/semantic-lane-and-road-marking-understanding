"""
Chấm điểm 3 chế độ input (image_only / json_only / image_json) trên model
chính hiện tại (ising-calibration-31b), N=199 ảnh - đây là bản MỚI của mục
4.4 báo cáo, dùng JSON đã sửa lỗi lane_count (output-v3) và prompt đã hoàn
thiện (llm_batch_client.py hiện tại).

Session mới ("session_3_ising31b") - KHÔNG lẫn với session_2 (dữ liệu model
cũ nemotron-8b, prompt cũ) hay model_comparison_full (so sánh model, không
phải so sánh mode).

Cần chạy TRƯỚC (sinh output, dùng llm_batch_client.py - DEFAULT_MODEL đã là
ising-31b, không cần truyền --model):
    python llm_batch_client.py --mode image_only \\
        --image-dir input --output-dir output-suggest-image-only-prompt-v5-31b
    python llm_batch_client.py --mode json_only \\
        --json-dir output-v3 --output-dir output-suggest-json-only-prompt-v5-31b
    (image_json đã có sẵn: output-suggest-image-json-prompt-v5-31b)

Rồi mới chạy script này (từ thư mục src-v2):
    python evaluate_mode_comparison_v5.py
"""

import os

from score_output_by_gemini import GEMINI_API_KEY, MODEL_NAME, OUTPUT_DIR, evaluate_all_experiments
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_FOLDER = os.path.join(BASE_DIR, "input")

EXPERIMENT_FOLDERS = {
    "prompt_image": os.path.join(BASE_DIR, "output-suggest-image-only-prompt-v5-31b"),
    "prompt_json": os.path.join(BASE_DIR, "output-suggest-json-only-prompt-v5-31b"),
    "prompt_image_json": os.path.join(BASE_DIR, "output-suggest-image-json-prompt-v5-31b"),
}

SESSION_NAME = "session_3_ising31b"


if __name__ == "__main__":
    setup_logging()

    if not GEMINI_API_KEY:
        logger.error(
            "Thiếu GEMINI_API_KEY - đặt biến môi trường GEMINI_API_KEY trước khi chạy."
        )
    else:
        missing = [name for name, folder in EXPERIMENT_FOLDERS.items() if not os.path.isdir(folder)]
        if missing:
            logger.error(
                f"Chưa có output cho: {missing} - chạy llm_batch_client.py sinh output trước "
                "(xem hướng dẫn ở đầu file này)."
            )
        else:
            evaluate_all_experiments(
                images_folder=IMAGES_FOLDER,
                experiment_folders=EXPERIMENT_FOLDERS,
                output_dir=OUTPUT_DIR,
                api_key=GEMINI_API_KEY,
                model_name=MODEL_NAME,
                session_name=SESSION_NAME,
                overwrite_existing=False,
            )
