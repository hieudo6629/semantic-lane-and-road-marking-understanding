"""
Đo độ trễ CPU của các biến thể YOLOv8 (n/s/m COCO và n TT100K) bằng model.predict()
trên 200 ảnh dữ liệu thực tế - bổ sung cho phép đo trên 200 ảnh CULane
(benchmark_cpu_latency.py, benchmark_yolov8n_predict.py), cùng quy trình đo.

Kết quả ghi vào evaluation_results/cpu_latency/yolo_variants_real_life.json.

Chạy (từ thư mục src-v2):
    python benchmark_yolo_variants_real_life.py
"""

import json
import os

from benchmark_cpu_latency import OUT_DIR, real_images, time_yolo_reference
from benchmark_yolov8n_predict import WEIGHTS as N_WEIGHTS

WEIGHTS = {"yolov8n_coco": N_WEIGHTS["yolov8n_coco"], "yolov8s_coco": "yolov8s.pt",
           "yolov8m_coco": "yolov8m.pt", "yolov8n_tt100k": N_WEIGHTS["yolov8n_tt100k"]}


def main():
    paths = real_images()
    result = {}
    for name, w in WEIGHTS.items():
        print(f"Đang đo {name}: {w}")
        result[name] = {"weights": w, **time_yolo_reference(w, paths)}
        print(json.dumps(result[name], indent=2, ensure_ascii=False))
    path = os.path.join(OUT_DIR, "yolo_variants_real_life.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Đã lưu: {path}")


if __name__ == "__main__":
    main()
