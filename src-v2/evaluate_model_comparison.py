"""
So sánh chất lượng output giữa 3 model NIM (nemotron-nano-8b gốc,
nemotron-nano-12b-v2-vl, ising-calibration-1.5-31b) trên bộ ảnh chẩn đoán
(diagnostic_set/), cùng mode image_json, dùng Gemini chấm điểm.

Tái dùng đúng logic chấm điểm trong score_output_by_gemini.py
(evaluate_all_experiments) - chỉ đổi tham số (thư mục ảnh nhỏ hơn, 3 thư mục
"thí nghiệm" là 3 MODEL thay vì 3 MODE), không sửa file gốc.

Cần biến môi trường GEMINI_API_KEY trước khi chạy.
"""

import os

from score_output_by_gemini import GEMINI_API_KEY, MODEL_NAME, OUTPUT_DIR, evaluate_all_experiments
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_FOLDER = os.path.join(BASE_DIR, "diagnostic_set", "input")

EXPERIMENT_FOLDERS = {
    "nemotron_nano_8b": os.path.join(BASE_DIR, "diagnostic_set", "output-image-json"),
    "nemotron_nano_12b": os.path.join(BASE_DIR, "diagnostic_set", "output-image-json-nemotron12b"),
    "ising_calibration_31b": os.path.join(BASE_DIR, "diagnostic_set", "output-image-json-ising"),
}

SESSION_NAME = "model_comparison_diagnostic"


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
