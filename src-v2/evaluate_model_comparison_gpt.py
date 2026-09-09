"""
Phân tích lần chạy đầu tiên của GPT-5 Mini làm judge (evaluation_results/gpt_judge/,
20 ảnh) - so với 2 mốc:
1. Điểm người chấm (human_agreement_sample.xlsx) - MỐC ĐÚNG để trả lời "judge nào
   chính xác hơn" (xem lý do ở score_output_by_gpt.py / mục 5 báo cáo).
2. Điểm Gemini đã chấm sẵn (evaluation_results/model_comparison_full/) - CHỈ để
   tham khảo mức độ 2 judge giống/khác nhau, KHÔNG dùng để kết luận judge nào tốt hơn.

Cách dùng (từ thư mục src-v2):
    python evaluate_model_comparison_gpt.py
"""

import json
import os
import sys

import pandas as pd

HUMAN_SAMPLE_PATH = "human_agreement_sample.xlsx"
GPT_DIR = "evaluation_results/gpt_judge"
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


def _agreement_stats(a: pd.Series, b: pd.Series) -> dict:
    diff = (a - b).abs()
    return {
        "n": len(a),
        "exact": (diff == 0).mean() * 100,
        "within_1": (diff <= 1).mean() * 100,
        "corr": a.corr(b),
        "mean_diff": (a - b).mean(),  # duong = a cao hon b trung binh
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    human_df = pd.read_excel(HUMAN_SAMPLE_PATH)
    human_df.columns = [c.strip() for c in human_df.columns]

    rows = []
    for _, row in human_df.iterrows():
        img = int(row["Image"])
        gpt_path = os.path.join(GPT_DIR, f"{img}.json")
        gemini_path = os.path.join(GEMINI_DIR, f"{img}.json")
        if not os.path.exists(gpt_path):
            print(f"Bỏ qua ảnh {img}: chưa có kết quả GPT ({gpt_path})")
            continue
        if not os.path.exists(gemini_path):
            print(f"Bỏ qua ảnh {img}: chưa có kết quả Gemini ({gemini_path})")
            continue

        with open(gpt_path, encoding="utf-8") as f:
            gpt_scores = json.load(f)[EXPERIMENT_KEY]["scores"]
        with open(gemini_path, encoding="utf-8") as f:
            gemini_scores = json.load(f)[EXPERIMENT_KEY]["scores"]

        for crit in CRITERIA:
            human_val = row.get(f"human_{crit}")
            if pd.isna(human_val):
                continue
            rows.append({
                "Image": img,
                "criterion": crit,
                "human_score": int(human_val),
                "gpt_score": int(gpt_scores[crit]["score"]),
                "gemini_score": int(gemini_scores[crit]["score"]),
            })

    result = pd.DataFrame(rows)
    n = len(result)
    if n == 0:
        print("Không có dữ liệu để so sánh.")
        return

    print(f"Tổng số cặp so sánh được: {n} (từ {result['Image'].nunique()} ảnh)\n")

    print("=" * 70)
    print("1. GPT-5 Mini vs NGƯỜI (mốc so sánh ĐÚNG để đánh giá judge nào chính xác hơn)")
    print("=" * 70)
    s = _agreement_stats(result["human_score"], result["gpt_score"])
    print(f"Đồng thuận tuyệt đối: {s['exact']:.1f}%")
    print(f"Đồng thuận trong sai số <=1: {s['within_1']:.1f}%")
    print(f"Tương quan Pearson: {s['corr']:.3f}")
    print(f"Chênh lệch trung bình (người - GPT): {s['mean_diff']:+.2f} (dương = người chấm cao hơn GPT)\n")

    print("So sánh với Gemini vs NGƯỜI đã đo trước đó (evaluate_human_agreement.py):")
    print("  Gemini: đồng thuận tuyệt đối 36.7%, trong sai số <=1: 79.2%, tương quan 0.427\n")

    print("Chi tiết GPT vs người theo từng tiêu chí:")
    for crit in CRITERIA:
        sub = result[result["criterion"] == crit]
        if len(sub) == 0:
            continue
        st = _agreement_stats(sub["human_score"], sub["gpt_score"])
        print(f"  {crit:28} n={st['n']:3} | khớp={st['exact']:5.1f}% | trong sai số 1={st['within_1']:5.1f}%")

    print()
    print("=" * 70)
    print("2. GPT-5 Mini vs Gemini (CHỈ để tham khảo, KHÔNG dùng kết luận judge nào tốt hơn)")
    print("=" * 70)
    s2 = _agreement_stats(result["gpt_score"], result["gemini_score"])
    print(f"Đồng thuận tuyệt đối: {s2['exact']:.1f}%")
    print(f"Đồng thuận trong sai số <=1: {s2['within_1']:.1f}%")
    print(f"Tương quan Pearson: {s2['corr']:.3f}")
    print(f"Chênh lệch trung bình (GPT - Gemini): {s2['mean_diff']:+.2f}\n")

    print("Các cặp GPT lệch NGƯỜI nhiều nhất (>=2 điểm):")
    result["diff_human_gpt"] = (result["human_score"] - result["gpt_score"]).abs()
    big = result[result["diff_human_gpt"] >= 2].sort_values("diff_human_gpt", ascending=False)
    if len(big) == 0:
        print("  (không có)")
    else:
        print(big[["Image", "criterion", "human_score", "gpt_score", "gemini_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
