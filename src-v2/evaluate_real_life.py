"""
Đánh giá module hiểu làn đường + biển báo trên bộ 200 ảnh dashcam thực tế
độc lập (input_real_life/output_real_life), đối chiếu với nhãn tay
new_image_labels.xlsx.

Mục đích: bộ này KHÔNG lấy từ CULane (nguồn model lane detection
culane_res34.pth được pretrain) - dùng để kiểm chứng độc lập, giải quyết rủi
ro data leakage đã nêu khi đánh giá trên 199 ảnh CULane.

Cách dùng (từ thư mục src-v2):
    python evaluate_real_life.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd

LABELS_PATH = "new_image_labels.xlsx"
JSON_DIR = "output_real_life"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    df = pd.read_excel(LABELS_PATH)
    df.columns = [c.strip() for c in df.columns]

    records = []
    missing = []
    for _, row in df.iterrows():
        img = int(row["Image"])
        path = os.path.join(JSON_DIR, f"{img}.json")
        if not os.path.exists(path):
            missing.append(img)
            continue
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        records.append({
            "Image": img,
            "true_lane_count": row["true_lane_count"],
            "false_lane_count": row["false_lane_count"],
            "opposite_lane_count": row["opposite_lane_count"],
            "true_road_type_code": row["true_road_type"],
            "true_road_value": row["true_road_value"],
            "ego_lane_correct": row["ego_lane_correct"],
            "true_sign_count": row["true_sign_count"],
            "correct_detection_count": row["correct_detection_count"],
            "false_detection_count": row["false_detection_count"],
            "pred_lane_count": d["road"]["geometry"]["lane_count"],
            "pred_road_type": d["road"]["road_type"],
        })

    if missing:
        print(f"Bỏ qua {len(missing)} ảnh không tìm thấy JSON: {missing[:10]}")

    r = pd.DataFrame(records)
    n = len(r)
    print(f"Tổng số ảnh đối chiếu được: {n}\n")

    hard_cases = r["true_road_type_code"] == 0

    print("=== 1. Độ chính xác lane_count ===")
    exact_match = (r["true_lane_count"] == r["pred_lane_count"]).mean()
    mae = (r["true_lane_count"] - r["pred_lane_count"]).abs().mean()
    print(f"Exact match: {exact_match * 100:.1f}%")
    print(f"MAE: {mae:.3f}")
    total_true = r["true_lane_count"].sum()
    total_false = r["false_lane_count"].sum()
    total_opp = r["opposite_lane_count"].sum()
    total_pred = total_true + total_false + total_opp
    if total_pred > 0:
        print(f"Precision (true / (true+false+opposite)): {total_true / total_pred * 100:.1f}%")
    print()

    print("=== 2. Độ chính xác road_type (loại 'khó phát hiện') ===")
    rt = r[~hard_cases].copy()
    exact_rt = (rt["true_road_value"] == rt["pred_road_type"]).mean()
    print(f"N={len(rt)}, Exact match: {exact_rt * 100:.1f}%")

    def bucket(x):
        if pd.isna(x):
            return "unknown"
        x = str(x)
        if "gentle" in x:
            return "gentle"
        if "sharp" in x:
            return "sharp"
        if x == "straight":
            return "straight"
        return "other"

    rt["true_b"] = rt["true_road_value"].apply(bucket)
    rt["pred_b"] = rt["pred_road_type"].apply(bucket)
    bucket_match = (rt["true_b"] == rt["pred_b"]).mean()
    print(f"Bucket match (bỏ qua hướng trái/phải): {bucket_match * 100:.1f}%")
    print(pd.crosstab(rt["true_b"], rt["pred_b"]))
    print()

    print("=== 3. ego_lane_correct ===")
    print(f"{r['ego_lane_correct'].mean() * 100:.1f}%")
    print()

    print("=== 4. Biển báo/đèn tín hiệu (Precision/Recall) ===")
    total_true_signs = r["true_sign_count"].sum()
    total_correct = r["correct_detection_count"].sum()
    total_false_det = r["false_detection_count"].sum()
    total_detected = total_correct + total_false_det
    precision = total_correct / total_detected if total_detected > 0 else float("nan")
    recall = total_correct / total_true_signs if total_true_signs > 0 else float("nan")
    print(f"Tổng biển thật (true_sign_count): {total_true_signs}")
    print(f"Tổng model phát hiện (correct+false): {total_detected}")
    print(f"Precision: {precision * 100:.1f}%")
    print(f"Recall: {recall * 100:.1f}%")


if __name__ == "__main__":
    main()
