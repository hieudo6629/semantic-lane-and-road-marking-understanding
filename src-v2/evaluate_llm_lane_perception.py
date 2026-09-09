"""
So sánh 3 nguồn nhận diện ngữ nghĩa làn đường trên cùng N=200 ảnh CULane:
    1. Nhãn tay (image_labels.xlsx)                      - ground truth
    2. Pipeline UFLD-v2 + xử lý ngữ nghĩa (output-v3/<tên>_brief.json)
    3. VLM tự nhận diện trực tiếp từ ảnh (output-llm-lane-perception/
       <tên>_llm_brief.json - sinh bởi llm_lane_perception.py)

Mục đích: trả lời câu hỏi "model VLM có thể tự phát hiện ngữ nghĩa làn đường
từ ảnh chính xác như tầng detection (UFLD-v2) hiện tại hay không?" - đặc
biệt trên nhóm ảnh mà UFLD-v2 thất bại do thiếu vạch kẻ (hard_reason != Normal,
xem mục 4.1 luận văn).

Cách dùng (từ thư mục src-v2):
    python evaluate_llm_lane_perception.py
    python evaluate_llm_lane_perception.py --labels new_image_labels.xlsx \\
        --pipeline-dir output_real_life --llm-dir output-llm-lane-perception-real-life
"""

import argparse
import json
import os
import sys

import pandas as pd


def _bucket_from_shape(road_shape: dict) -> str:
    """type/severity/direction (schema _brief.json) -> 1 chuỗi bucket để so sánh."""
    t = (road_shape or {}).get("type")
    if t != "curve":
        return t or "unknown"
    severity = road_shape.get("severity")
    direction = road_shape.get("direction")
    return f"{severity}_{direction}"


def _bucket_from_true_value(true_road_value) -> str:
    """true_road_value (vd 'gentle_left_curve','straight') -> cung dinh dang bucket voi tren."""
    if pd.isna(true_road_value):
        return "unknown"
    v = str(true_road_value)
    if v == "straight":
        return "straight"
    if "gentle" in v:
        severity = "gentle"
    elif "sharp" in v:
        severity = "sharp"
    else:
        return "unknown"
    direction = "left" if "left" in v else "right" if "right" in v else "unknown"
    return f"{severity}_{direction}"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, AttributeError):
            pass

    parser = argparse.ArgumentParser(description="So sanh 3 nguon nhan dien lan duong: nhan tay / pipeline UFLD-v2 / LLM")
    parser.add_argument("--labels", type=str, default="image_labels.xlsx")
    parser.add_argument("--pipeline-dir", type=str, default="output-v3")
    parser.add_argument("--llm-dir", type=str, default="output-llm-lane-perception")
    args = parser.parse_args()

    df = pd.read_excel(args.labels)
    df.columns = [c.strip() for c in df.columns]
    has_hard_reason = "hard_reason_value" in df.columns

    rows = []
    missing_pipeline, missing_llm = [], []
    for _, row in df.iterrows():
        img = int(row["Image"])

        pipeline_path = os.path.join(args.pipeline_dir, f"{img}_brief.json")
        llm_path = os.path.join(args.llm_dir, f"{img}_llm_brief.json")
        if not os.path.exists(pipeline_path):
            missing_pipeline.append(img)
            continue
        if not os.path.exists(llm_path):
            missing_llm.append(img)
            continue

        with open(pipeline_path, encoding="utf-8") as f:
            pipe = json.load(f)
        with open(llm_path, encoding="utf-8") as f:
            llm = json.load(f)

        rows.append({
            "Image": img,
            "hard_reason": row["hard_reason_value"] if has_hard_reason else "Normal",
            "true_lane_count": row["true_lane_count"],
            "true_road_bucket": _bucket_from_true_value(row["true_road_value"]),
            "pipe_lane_count": pipe.get("lane_count"),
            "pipe_road_bucket": _bucket_from_shape(pipe.get("road_shape")),
            "pipe_ego_position": (pipe.get("ego_lane") or {}).get("position"),
            "llm_lane_count": llm.get("lane_count"),
            "llm_road_bucket": _bucket_from_shape(llm.get("road_shape")),
            "llm_ego_position": (llm.get("ego_lane") or {}).get("position"),
        })

    if missing_pipeline:
        print(f"Bo qua {len(missing_pipeline)} anh thieu output-v3 brief: {missing_pipeline[:5]}")
    if missing_llm:
        print(f"Bo qua {len(missing_llm)} anh thieu output-llm-lane-perception: {missing_llm[:5]}")

    r = pd.DataFrame(rows)
    n = len(r)
    print(f"\nTong so anh doi chieu duoc: {n}\n")

    def report(sub: pd.DataFrame, label: str) -> None:
        ns = len(sub)
        if ns == 0:
            print(f"--- {label} (N=0) ---\n")
            return
        pipe_exact = (sub["true_lane_count"] == sub["pipe_lane_count"]).sum()
        llm_exact = (sub["true_lane_count"] == sub["llm_lane_count"]).sum()
        pipe_mae = (sub["true_lane_count"] - sub["pipe_lane_count"]).abs().mean()
        llm_mae = (sub["true_lane_count"] - sub["llm_lane_count"]).abs().mean()
        pipe_road = (sub["true_road_bucket"] == sub["pipe_road_bucket"]).sum()
        llm_road = (sub["true_road_bucket"] == sub["llm_road_bucket"]).sum()
        ego_agree = (sub["pipe_ego_position"] == sub["llm_ego_position"]).sum()

        print(f"--- {label} (N={ns}) ---")
        print(f"  Lane count exact match : pipeline {pipe_exact}/{ns}={pipe_exact/ns*100:.1f}%  |  LLM {llm_exact}/{ns}={llm_exact/ns*100:.1f}%")
        print(f"  Lane count MAE         : pipeline {pipe_mae:.3f}  |  LLM {llm_mae:.3f}")
        print(f"  Road shape bucket match: pipeline {pipe_road}/{ns}={pipe_road/ns*100:.1f}%  |  LLM {llm_road}/{ns}={llm_road/ns*100:.1f}%")
        print(f"  Ego position dong y giua pipeline va LLM (khong co ground truth doc lap): {ego_agree}/{ns}={ego_agree/ns*100:.1f}%")
        print()

    report(r, "TOAN BO N=200")
    if has_hard_reason:
        report(r[r["hard_reason"] == "Normal"], "Nhom Normal (co vach ke ro)")
        report(r[r["hard_reason"] != "Normal"], "Nhom Hard (khong vach ke ro - noi UFLD-v2 that bai)")

        print("=== Chi tiet nhom Hard theo tung anh (true vs pipeline vs LLM lane_count) ===")
        hard = r[r["hard_reason"] != "Normal"]
        print(hard[["Image", "hard_reason", "true_lane_count", "pipe_lane_count", "llm_lane_count"]].to_string(index=False))
    else:
        print("(Khong co cot hard_reason_value trong file nhan - bo qua breakdown Normal/Hard)")


if __name__ == "__main__":
    main()
