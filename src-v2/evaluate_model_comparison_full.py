"""
So sánh chất lượng output giữa 2 model NIM (nemotron-nano-8b gốc,
ising-calibration-1.5-31b) trên TOÀN BỘ 199 ảnh, cùng mode image_json, dùng
Gemini chấm điểm.

Không đưa nemotron-nano-12b-v2-vl vào so sánh này - loại vì tỉ lệ lỗi 82.9%
(165/199) trên batch thật (xem output-suggest-image-json-prompt-v5-12b/
_summary.json), mẫu thành công còn lại quá nhỏ/thiên lệch để so sánh công bằng.

Tái dùng logic chấm điểm trong score_output_by_gemini.py, không sửa file gốc.

Cần biến môi trường GEMINI_API_KEY trước khi chạy.
"""

import os

from score_output_by_gemini import GEMINI_API_KEY, MODEL_NAME, OUTPUT_DIR, evaluate_all_experiments
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_FOLDER = os.path.join(BASE_DIR, "input")

EXPERIMENT_FOLDERS = {
    "nemotron_nano_8b": os.path.join(BASE_DIR, "output-suggest-prompt-v4"),
    "ising_calibration_31b": os.path.join(BASE_DIR, "output-suggest-image-json-prompt-v5-31b"),
}

SESSION_NAME = "model_comparison_full"


if __name__ == "__main__":
    setup_logging()

    if not GEMINI_API_KEY:
        logger.error(
            "Thiếu GEMINI_API_KEY - đặt biến môi trường GEMINI_API_KEY trước khi chạy."
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
