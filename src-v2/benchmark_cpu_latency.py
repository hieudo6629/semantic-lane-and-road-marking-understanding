"""
Đo độ trễ CPU của mô-đun trích xuất SSI, tách riêng từng thành phần (luận văn,
phương án 1 trả lời câu hỏi "vì sao chọn UFLD-v2 và YOLOv8n").

Thành phần được đo cho TỪNG ảnh (batch size 1, chỉ CPU):
    lane   : LaneDetector.detect()  - UFLD-v2 ResNet-34 (tiền xử lý + forward + giải mã)
    sign   : SignDetector.detect()  - YOLOv8n TT100K (letterbox 640 + forward + NMS)
    semantic: SceneBuilder.build() + summarize_scene() - bước biểu diễn ngữ nghĩa -> SSI
    total  : tổng ba thành phần trên (không tính đọc file, không vẽ hình)

Đối chiếu kích thước YOLOv8 (chỉ đo độ trễ, không đo độ chính xác): YOLOv8s, YOLOv8m
trọng số COCO chính thức (Ultralytics tự tải về nếu chưa có), imgsz 640, cùng ảnh CULane.

Quy trình: bỏ WARMUP lượt chạy đầu (trên ảnh đầu tiên của tập), sau đó mỗi ảnh chạy
1 lần; báo cáo mean ± SD, median, P95 (ms). Không ghi đè bất kỳ kết quả nào của
pipeline - chỉ ghi file kết quả đo vào evaluation_results/cpu_latency/.

Chạy (từ thư mục src-v2):
    python benchmark_cpu_latency.py
"""

import json
import os
import platform
import time

import cv2
import numpy as np
import torch

from analysis.scene_summarizer import summarize_scene
from main import build_pipeline_config, load_raw_config
from pipeline import TrafficScenePipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CULANE_DIR = os.path.join(BASE_DIR, "input")
CULANE_STEMS_DIR = os.path.join(BASE_DIR, "output-v3")  # 200 ảnh CULane dùng trong luận văn
REAL_DIR = os.path.join(BASE_DIR, "input_real_life")
OUT_DIR = os.path.join(BASE_DIR, "evaluation_results", "cpu_latency")
WARMUP = 10
YOLO_REFERENCE = ["yolov8s.pt", "yolov8m.pt"]


def culane_images():
    stems = sorted(int(f.split("_")[0]) for f in os.listdir(CULANE_STEMS_DIR) if f.endswith("_brief.json"))
    return [os.path.join(CULANE_DIR, f"{s}.jpg") for s in stems]


def real_images():
    return [os.path.join(REAL_DIR, f) for f in sorted(os.listdir(REAL_DIR), key=lambda x: int(os.path.splitext(x)[0]))
            if f.lower().endswith((".jpg", ".png"))]


def stats_ms(values):
    a = np.array(values) * 1000.0
    return {"n": int(a.size), "mean": float(a.mean()), "sd": float(a.std(ddof=1)),
            "median": float(np.median(a)), "p95": float(np.percentile(a, 95))}


def time_pipeline(pipe, paths):
    times = {"lane": [], "sign": [], "semantic": [], "total": []}
    warm = cv2.imread(paths[0])
    for _ in range(WARMUP):
        lanes = pipe.lane_detector.detect(warm)
        signs = pipe.sign_detector.detect(warm, warm.shape[1], warm.shape[0])
        summarize_scene(pipe.scene_builder.build(lanes, warm.shape[1], warm.shape[0], detected_signs=signs).to_dict())
    for p in paths:
        img = cv2.imread(p)
        h, w = img.shape[:2]
        t0 = time.perf_counter()
        lanes = pipe.lane_detector.detect(img)
        t1 = time.perf_counter()
        signs = pipe.sign_detector.detect(img, w, h)
        t2 = time.perf_counter()
        summarize_scene(pipe.scene_builder.build(lanes, w, h, detected_signs=signs).to_dict())
        t3 = time.perf_counter()
        times["lane"].append(t1 - t0)
        times["sign"].append(t2 - t1)
        times["semantic"].append(t3 - t2)
        times["total"].append(t3 - t0)
    return {k: stats_ms(v) for k, v in times.items()}


def time_yolo_reference(weights, paths):
    from ultralytics import YOLO
    model = YOLO(weights)
    warm = cv2.imread(paths[0])
    for _ in range(WARMUP):
        model.predict(warm, imgsz=640, device="cpu", verbose=False)
    ts = []
    for p in paths:
        img = cv2.imread(p)
        t0 = time.perf_counter()
        model.predict(img, imgsz=640, device="cpu", verbose=False)
        ts.append(time.perf_counter() - t0)
    return stats_ms(ts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pipe = TrafficScenePipeline(build_pipeline_config(load_raw_config()))
    result = {
        "environment": {
            "cpu": platform.processor(), "os": platform.platform(), "python": platform.python_version(),
            "torch": torch.__version__, "torch_threads": torch.get_num_threads(), "warmup": WARMUP,
        },
        "culane": time_pipeline(pipe, culane_images()),
        "real_life": time_pipeline(pipe, real_images()),
        "yolo_reference_culane": {w: time_yolo_reference(w, culane_images()) for w in YOLO_REFERENCE},
    }
    path = os.path.join(OUT_DIR, "cpu_latency.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nĐã lưu: {path}")


if __name__ == "__main__":
    main()
