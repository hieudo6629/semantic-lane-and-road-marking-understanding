"""
So sánh điểm chấm tay (human_agreement_sample.xlsx) với điểm Gemini đã chấm
sẵn (evaluation_results/model_comparison_full/<ten>.json, thí nghiệm
ising_calibration_31b) trên cùng 20 ảnh - đo độ đồng thuận giữa LLM-as-judge
và người, xem mục 5 báo cáo tiến độ.

Cách dùng (từ thư mục src-v2, sau khi đã điền cột human_* trong file xlsx):
    python evaluate_human_agreement.py
"""

import json
import os
import sys

import pandas as pd

SAMPLE_PATH = "human_agreement_sample.xlsx"
GEMINI_DIR = "evaluation_results/model_comparison_full"
EXPERIMENT_KEY = "ising_calibration_31b"

CRITERIA = [
    "situation_understanding",
    "road_understanding",
    "lane_ego_position",
    "traffic_sign_rule",
    "driving_recommendation",
    "safety_considerations",
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    df = pd.read_excel(SAMPLE_PATH)
    df.columns = [c.strip() for c in df.columns]

    rows = []
    for _, row in df.iterrows():
        img = int(row["Image"])
        gemini_path = os.path.join(GEMINI_DIR, f"{img}.json")
        if not os.path.exists(gemini_path):
            print(f"Bỏ qua ảnh {img}: không tìm thấy điểm Gemini tại {gemini_path}")
            continue
        with open(gemini_path, encoding="utf-8") as f:
            gemini_scores = json.load(f)[EXPERIMENT_KEY]["scores"]

        for crit in CRITERIA:
            human_col = f"human_{crit}"
            human_val = row.get(human_col)
            if pd.isna(human_val):
                continue
            rows.append({
                "Image": img,
                "criterion": crit,
                "human_score": int(human_val),
                "gemini_score": int(gemini_scores[crit]["score"]),
            })

    result = pd.DataFrame(rows)
    n = len(result)
    if n == 0:
        print("Chưa có điểm chấm tay nào (cột human_* còn trống). Điền xong rồi chạy lại.")
        return

    result["diff"] = (result["human_score"] - result["gemini_score"]).abs()
    exact_agree = (result["diff"] == 0).mean()
    within_1 = (result["diff"] <= 1).mean()
    correlation = result["human_score"].corr(result["gemini_score"])

    print(f"Tổng số cặp điểm so sánh được: {n} (từ {result['Image'].nunique()} ảnh x tối đa 6 tiêu chí)\n")
    print(f"Đồng thuận tuyệt đối (điểm khớp chính xác): {exact_agree * 100:.1f}%")
    print(f"Đồng thuận trong sai số <=1 điểm: {within_1 * 100:.1f}%")
    print(f"Hệ số tương quan (Pearson): {correlation:.3f}\n")

    print("Chi tiết theo từng tiêu chí:")
    for crit in CRITERIA:
        sub = result[result["criterion"] == crit]
        if len(sub) == 0:
            continue
        print(
            f"  {crit:28} n={len(sub):3} | khớp chính xác={((sub['diff']==0).mean()*100):5.1f}% "
            f"| trong sai số 1={((sub['diff']<=1).mean()*100):5.1f}%"
        )

    print("\nCác cặp lệch nhiều nhất (chênh >=2 điểm) - đáng xem lại:")
    big_diff = result[result["diff"] >= 2].sort_values("diff", ascending=False)
    if len(big_diff) == 0:
        print("  (không có)")
    else:
        print(big_diff[["Image", "criterion", "human_score", "gemini_score", "diff"]].to_string(index=False))


if __name__ == "__main__":
    main()
