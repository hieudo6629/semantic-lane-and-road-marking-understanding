"""
Chấm điểm 3 chế độ input (image_only/json_only/image_json, model ising-31b,
N=199 ảnh) bằng DeepSeek - bản DeepSeek của evaluate_mode_comparison_v5.py,
dùng cùng 1 request/ảnh (gộp 3 mode) để tiết kiệm chi phí.

Cần chạy SAU khi cả 3 thư mục output-suggest-*-prompt-v5-31b đã đủ 199 ảnh,
VÀ sau khi đã xác nhận model DeepSeek hỗ trợ vision qua
`python score_output_by_deepseek.py --test-only`.

Cách dùng (từ thư mục src-v2):
    python evaluate_mode_comparison_v5_deepseek.py
"""

import os

from score_output_by_deepseek import DEFAULT_MODEL, evaluate_all_experiments
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, "input")

EXPERIMENT_FOLDERS = {
    "prompt_image": os.path.join(BASE_DIR, "output-suggest-image-only-prompt-v5-31b"),
    "prompt_json": os.path.join(BASE_DIR, "output-suggest-json-only-prompt-v5-31b"),
    "prompt_image_json": os.path.join(BASE_DIR, "output-suggest-image-json-prompt-v5-31b"),
}

OUTPUT_DIR = os.path.join(BASE_DIR, "evaluation_results", "mode_comparison_deepseek")


if __name__ == "__main__":
    setup_logging()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("Thiếu DEEPSEEK_API_KEY.")
    else:
        missing = [name for name, folder in EXPERIMENT_FOLDERS.items() if not os.path.isdir(folder)]
        if missing:
            logger.error(f"Chưa có output cho: {missing} - chạy llm_batch_client.py trước.")
        else:
            evaluate_all_experiments(
                images_folder=IMAGES_FOLDER,
                experiment_folders=EXPERIMENT_FOLDERS,
                output_dir=OUTPUT_DIR,
                api_key=api_key,
                model=DEFAULT_MODEL,
                overwrite_existing=False,
                delay=2.0,
            )
