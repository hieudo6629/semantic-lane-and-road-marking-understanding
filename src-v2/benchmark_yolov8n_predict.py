"""
Đo lại độ trễ CPU của YOLOv8n bằng model.predict() trực tiếp - cùng quy trình với
YOLOv8s/YOLOv8m trong benchmark_cpu_latency.py - để so sánh các kích thước YOLOv8
trong cùng điều kiện (200 ảnh CULane, imgsz 640, batch 1, CPU, bỏ 10 lượt khởi động).

Hai trọng số được đo:
    - yolov8n TT100K (model dùng trong luận văn, đường dẫn trong configs/config.yaml)
    - yolov8n COCO gốc (../model/yolov8n.pt) - cùng loại trọng số với YOLOv8s/m đã đo

Kết quả ghi vào evaluation_results/cpu_latency/yolov8n_predict.json.

Chạy (từ thư mục src-v2):
    python benchmark_yolov8n_predict.py
"""

import json
import os

from benchmark_cpu_latency import OUT_DIR, culane_images, time_yolo_reference
from main import _resolve_path, load_raw_config

WEIGHTS = {
    "yolov8n_tt100k": _resolve_path(load_raw_config()["models"]["sign_model_path"]),
    "yolov8n_coco": os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model", "yolov8n.pt")),
}


def main():
    paths = culane_images()
    result = {}
    for name, w in WEIGHTS.items():
        print(f"Đang đo {name}: {w}")
        result[name] = {"weights": w, **time_yolo_reference(w, paths)}
        print(json.dumps(result[name], indent=2, ensure_ascii=False))
    path = os.path.join(OUT_DIR, "yolov8n_predict.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Đã lưu: {path}")


if __name__ == "__main__":
    main()
