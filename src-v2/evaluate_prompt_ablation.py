"""
Chấm điểm 3 biến thể PROMPT (current / p1_minimal / p2_minimal_structured) -
CẢ 3 dùng CÙNG 1 input (ảnh + JSON, mode image_json) và CÙNG model chính hiện
tại (ising-calibration-31b, xem llm_batch_client.DEFAULT_MODEL), N=200 ảnh.
Đây là thí nghiệm kiểm chứng ảnh hưởng của ĐỘ PHỨC TẠP PROMPT (không phải
input mode như evaluate_mode_comparison_v5.py), dùng lại hạ tầng chấm điểm
của score_output_by_gemini.py.

3 biến thể:
    current                : prompt sản xuất hiện tại (llm_batch_client.DEFAULT_PROMPTS),
                              output đã có sẵn ở output-suggest-image-json-prompt-v5-31b -
                              KHÔNG cần chạy lại.
    p1_minimal              : prompt tối giản - chỉ đọc ảnh + JSON, không yêu cầu
                              cấu trúc đầu ra (xem prompt_p1_minimal.txt).
    p2_minimal_structured   : như p1 + yêu cầu cấu trúc đầu ra 3 phần (Situation
                              Assessment / Driving Recommendation / Safety
                              Considerations) - xem prompt_p2_minimal_structured.txt.

Vì cả 3 biến thể nhận CÙNG 1 input, đoạn hướng dẫn chấm điểm gốc trong
score_output_by_gemini.EVALUATION_INSTRUCTIONS (giả định 3 thí nghiệm có
quyền truy cập input KHÁC NHAU - image_only/json_only/image_json) không đúng
ở đây - ghi đè lại đoạn đó (giữ nguyên phần tiêu chí/thang điểm/luật chấm còn
lại) trước khi gọi evaluate_all_experiments().

Cần chạy TRƯỚC (sinh output cho p1/p2 - "current" đã có sẵn, không cần chạy lại):
    python llm_batch_client.py --mode image_json --image-dir input --json-dir output-v3 \\
        --prompt-file prompt_p1_minimal.txt --output-dir output-prompt-ablation-p1
    python llm_batch_client.py --mode image_json --image-dir input --json-dir output-v3 \\
        --prompt-file prompt_p2_minimal_structured.txt --output-dir output-prompt-ablation-p2

Rồi mới chạy script này (từ thư mục src-v2, cần biến môi trường GEMINI_API_KEY):
    python evaluate_prompt_ablation.py
"""

import os

import score_output_by_gemini as sog
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_FOLDER = os.path.join(BASE_DIR, "input")

EXPERIMENT_FOLDERS = {
    "current": os.path.join(BASE_DIR, "output-suggest-image-json-prompt-v5-31b"),
    "p1_minimal": os.path.join(BASE_DIR, "output-prompt-ablation-p1"),
    "p2_minimal_structured": os.path.join(BASE_DIR, "output-prompt-ablation-p2"),
}

SESSION_NAME = "session_prompt_ablation"

# Ghi đè hướng dẫn chấm điểm: bỏ đoạn giả định 3 thí nghiệm có quyền truy cập
# input KHÁC NHAU (đúng cho so sánh input mode, SAI cho so sánh prompt trong
# CÙNG 1 mode như ở đây) - giữ nguyên phần tiêu chí/thang điểm/luật chấm còn lại.
sog.EVALUATION_INSTRUCTIONS = sog.EVALUATION_INSTRUCTIONS.replace(
    """Evaluate each output according to the information available to that experiment:
- Image Only had access only to the image.
- JSON Only had access only to the semantic JSON.
- Image + JSON had access to both.

Do not penalize an output for failing to mention information that was unavailable to its input.""",
    """All outputs were generated from the SAME image and the SAME semantic JSON as input; only the prompt instructions given to the model differ between experiments. Score each output purely on its own correctness and evidence use - do not reward or penalize an output merely for following a different response format or being more or less structured.""",
)

if __name__ == "__main__":
    setup_logging()

    if not sog.GEMINI_API_KEY:
        logger.error(
            "Thiếu GEMINI_API_KEY - đặt biến môi trường GEMINI_API_KEY trước khi chạy."
        )
    else:
        missing = [name for name, folder in EXPERIMENT_FOLDERS.items() if not os.path.isdir(folder)]
        if missing:
            logger.error(
                f"Chưa có output cho: {missing} - chạy llm_batch_client.py sinh output p1/p2 trước "
                "(xem hướng dẫn ở đầu file này)."
            )
        else:
            sog.evaluate_all_experiments(
                images_folder=IMAGES_FOLDER,
                experiment_folders=EXPERIMENT_FOLDERS,
                output_dir=sog.OUTPUT_DIR,
                api_key=sog.GEMINI_API_KEY,
                model_name=sog.MODEL_NAME,
                session_name=SESSION_NAME,
                overwrite_existing=False,
            )
