"""
Thống kê kiểm định so sánh 3 biến thể prompt (current/p1_minimal/
p2_minimal_structured) từ kết quả chấm điểm của evaluate_prompt_ablation.py
(session_prompt_ablation) - tính điểm trung bình 6 tiêu chí/ảnh cho mỗi biến
thể, rồi kiểm định từng cặp bằng Wilcoxon signed-rank (test chính) + paired
t-test (đối chiếu) + Cohen's d, đúng phương pháp Mục 3.5.5 của luận văn.

Chạy (từ thư mục src-v2, SAU KHI đã chạy evaluate_prompt_ablation.py):
    python analyze_prompt_ablation_stats.py
"""

import json
import os
from itertools import combinations

import numpy as np
from scipy import stats

from score_output_by_gemini import EVALUATION_CRITERIA, OUTPUT_DIR

SESSION_NAME = "session_prompt_ablation"
SESSION_DIR = os.path.join(OUTPUT_DIR, SESSION_NAME)


def load_per_image_scores(session_dir: str) -> dict:
    """Trả về {tên_thí_nghiệm: {tên_ảnh: điểm trung bình 6 tiêu chí}}."""
    per_exp_scores: dict = {}
    for fname in sorted(os.listdir(session_dir)):
        if not fname.endswith(".json") or fname.startswith("_") or fname == "config.json":
            continue
        with open(os.path.join(session_dir, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        image_name = fname[:-5]
        for exp_name, exp_result in data.items():
            if exp_name.startswith("_") or not isinstance(exp_result, dict):
                continue
            scores = exp_result.get("scores", {})
            values = [scores[k]["score"] for k in EVALUATION_CRITERIA if k in scores]
            if len(values) != len(EVALUATION_CRITERIA):
                continue
            per_exp_scores.setdefault(exp_name, {})[image_name] = sum(values) / len(values)
    return per_exp_scores


def paired_arrays(per_exp_scores: dict, exp_a: str, exp_b: str):
    """Ghép cặp theo TÊN ẢNH CHUNG giữa 2 thí nghiệm (cùng thứ tự cho cả 2 mảng)."""
    common = sorted(set(per_exp_scores[exp_a]) & set(per_exp_scores[exp_b]))
    a = np.array([per_exp_scores[exp_a][img] for img in common])
    b = np.array([per_exp_scores[exp_b][img] for img in common])
    return a, b, common


def cohens_d_paired(a: np.ndarray, b: np.ndarray) -> float:
    diff = a - b
    sd = diff.std(ddof=1)
    return float(diff.mean() / sd) if sd > 0 else 0.0


def main() -> None:
    if not os.path.isdir(SESSION_DIR):
        print(f"Không tìm thấy thư mục session: {SESSION_DIR} - chạy evaluate_prompt_ablation.py trước.")
        return

    per_exp_scores = load_per_image_scores(SESSION_DIR)
    exp_names = sorted(per_exp_scores)
    if len(exp_names) < 2:
        print(f"Chỉ tìm thấy {len(exp_names)} thí nghiệm có điểm hợp lệ - cần >= 2 để so sánh.")
        return

    print("=" * 78)
    print("ĐIỂM TRUNG BÌNH 6 TIÊU CHÍ / ẢNH THEO TỪNG BIẾN THỂ PROMPT")
    print("=" * 78)
    for exp in exp_names:
        values = np.array(list(per_exp_scores[exp].values()))
        print(f"{exp:<24} N={len(values):<4} mean={values.mean():.3f}  sd={values.std(ddof=1):.3f}")

    print()
    print("=" * 78)
    print("KIỂM ĐỊNH CẶP (Wilcoxon signed-rank + paired t-test + Cohen's d)")
    print("=" * 78)
    for exp_a, exp_b in combinations(exp_names, 2):
        a, b, common = paired_arrays(per_exp_scores, exp_a, exp_b)
        if len(common) < 2:
            print(f"{exp_a} vs {exp_b}: không đủ ảnh chung ({len(common)}) để kiểm định.")
            continue
        w_stat, w_p = stats.wilcoxon(a, b)
        t_stat, t_p = stats.ttest_rel(a, b)
        d = cohens_d_paired(a, b)
        print(
            f"{exp_a} vs {exp_b} (N={len(common)}): "
            f"mean {a.mean():.3f} vs {b.mean():.3f} | "
            f"Wilcoxon p={w_p:.4g} | paired t={t_stat:.3f}, p={t_p:.4g} | Cohen's d={d:.3f}"
        )


if __name__ == "__main__":
    main()
