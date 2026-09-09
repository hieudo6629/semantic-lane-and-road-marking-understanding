"""
So sánh road_condition (proxy hiện tại, dựa trên ego_lane.confidence +
curvature.confidence - xem analysis/scene_summarizer.py) với nhãn tay
true_road_condition trong image_labels.xlsx.

Mục đích: trả lời câu hỏi "proxy hiện tại khớp với đánh giá bằng mắt tới đâu?"
TRƯỚC KHI quyết định có đáng công sửa sâu perception/lane_detector.py để lấy
tín hiệu confidence thật (exist_row/exist_col, độ nhọn phân bố vị trí) hay
không - xem phần trao đổi trước đó.

Cách dùng (chạy từ thư mục src-v2):
    python evaluate_road_condition.py
    python evaluate_road_condition.py --json-dir output-v3 --labels image_labels.xlsx
"""

import argparse
import json
import os
import sys

import pandas as pd

from analysis.scene_summarizer import summarize_scene

# Nhãn tay dùng mã số 1/2/3 (giống quy ước cột true_road_type trước đó),
# không phải chuỗi good/normal/poor trực tiếp - quy đổi trước khi so sánh.
CONDITION_CODE_MAP = {"1": "good", "2": "normal", "3": "poor"}


def _normalize_true_value(raw) -> str:
    text = str(raw).strip().lower()
    text = text[:-2] if text.endswith(".0") else text  # pandas đọc số nguyên có thể ra dạng "1.0"
    return CONDITION_CODE_MAP.get(text, text)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    parser = argparse.ArgumentParser(description="So sánh road_condition proxy với nhãn tay true_road_condition")
    parser.add_argument("--json-dir", type=str, default="output-v3", help="Thư mục chứa <ten>.json (scene thô)")
    parser.add_argument("--labels", type=str, default="image_labels.xlsx", help="File nhãn tay")
    args = parser.parse_args()

    df = pd.read_excel(args.labels)
    df.columns = [c.strip() for c in df.columns]

    if "true_road_condition" not in df.columns:
        print(f"CHƯA CÓ cột 'true_road_condition' trong {args.labels}. "
              "Thêm cột này (good/normal/poor) rồi chạy lại script.")
        return

    df = df.dropna(subset=["true_road_condition"])
    if df.empty:
        print("Cột 'true_road_condition' chưa có dữ liệu nào (toàn bộ đang trống).")
        return

    rows = []
    missing = []
    for _, row in df.iterrows():
        image = str(int(row["Image"])) if str(row["Image"]).replace(".0", "").isdigit() else str(row["Image"])
        json_path = os.path.join(args.json_dir, f"{image}.json")
        if not os.path.exists(json_path):
            missing.append(image)
            continue
        with open(json_path, encoding="utf-8") as f:
            scene = json.load(f)
        brief = summarize_scene(scene)
        rows.append({
            "image": image,
            "true": _normalize_true_value(row["true_road_condition"]),
            "predicted": brief["road_condition"]["level"],
            "detection_confidence": brief["road_condition"]["detection_confidence"],
        })

    if missing:
        print(f"Bỏ qua {len(missing)} ảnh không tìm thấy JSON trong {args.json_dir}: {missing[:10]}")

    result = pd.DataFrame(rows)
    n = len(result)
    if n == 0:
        print("Không có dòng nào để so sánh.")
        return

    print(f"Tổng số ảnh có nhãn 'true_road_condition' + JSON tương ứng: {n}\n")

    exact_match = (result["true"] == result["predicted"]).mean()
    print(f"Exact match (proxy khớp đúng nhãn tay): {exact_match * 100:.1f}%\n")

    print("Confusion matrix (hàng = nhãn tay thật, cột = proxy hiện tại):")
    print(pd.crosstab(result["true"], result["predicted"]))
    print()

    unknown_rate = (result["predicted"] == "unknown").mean()
    if unknown_rate > 0:
        print(f"Lưu ý: {unknown_rate * 100:.1f}% ảnh proxy trả 'unknown' (không có làn để tính) - "
              "loại khỏi so sánh exact-match phía trên nếu muốn đánh giá công bằng hơn:")
        known = result[result["predicted"] != "unknown"]
        if len(known) > 0:
            print(f"  Exact match trên {len(known)} ảnh CÓ predicted (loại 'unknown'): "
                  f"{(known['true'] == known['predicted']).mean() * 100:.1f}%")


if __name__ == "__main__":
    main()
