"""
Trích frame / detect biển báo-đèn giao thông từ video hành trình (dashcam).

Dùng lại SignDetector có sẵn (perception/sign_detector.py) - KHÔNG dùng
TrafficScenePipeline vì pipeline đó còn load thêm lane_detector (UFLD-v2),
nặng và không cần thiết cho việc chỉ detect biển báo/đèn trên video.

Cách dùng:
    # Trích 1 frame/giây từ video, chạy detect, lưu ảnh + JSON kết quả
    python video_sign_detect.py --video "C:/.../VID_095.MOV" --extract-frames --interval-sec 1

    # Xem detect thời gian thực (đọc file video, có cửa sổ preview), nhấn 'q' để thoát
    python video_sign_detect.py --video "C:/.../VID_095.MOV" --realtime

    # Thời gian thực + lưu lại video đã vẽ box + JSON kết quả từng frame
    python video_sign_detect.py --video "C:/.../VID_095.MOV" --realtime --save-video out.mp4 --save-json out.json

Ghi chú quan trọng: threshold mặc định lấy từ configs/config.yaml
(sign_detection.confidence_threshold = 0.5), nhưng qua test thực tế trên ảnh
dashcam, ngưỡng này quá chặt - phần lớn detection thật rơi vào khoảng
0.1-0.3 confidence. Nên thử --conf 0.15 đến 0.2 khi chạy trên video thật.
"""

import argparse
import json
import os
from typing import Dict, List, Optional, Tuple

import cv2
import yaml

from perception.sign_detector import DetectedSign, SignDetector
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs", "config.yaml")

# Màu vẽ box theo mức ưu tiên (BGR) - đỏ cho critical (stop/đèn đỏ), vàng cho
# warning (biển tốc độ/nhường đường), xanh lá cho các loại còn lại.
_COLOR_CRITICAL = (0, 0, 255)
_COLOR_WARNING = (0, 200, 255)
_COLOR_INFO = (0, 200, 0)


def _load_raw_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(os.path.dirname(CONFIG_PATH), path))


def build_sign_detector(conf_override: Optional[float]) -> SignDetector:
    """Khởi tạo SignDetector từ configs/config.yaml, cho phép ghi đè confidence_threshold bằng --conf."""
    raw = _load_raw_config()
    models = raw.get("models", {})
    conf = conf_override
    if conf is None:
        conf = raw.get("sign_detection", {}).get("confidence_threshold", 0.5)
    return SignDetector(
        model_path=_resolve_path(models["sign_model_path"]),
        confidence_threshold=conf,
        device=models.get("device", "cpu"),
    )


def _box_color(sign_type: str, detector: SignDetector) -> Tuple[int, int, int]:
    priority = detector.get_priority(sign_type)
    if priority <= 1:
        return _COLOR_CRITICAL
    if priority <= 10:
        return _COLOR_WARNING
    return _COLOR_INFO


def draw_detections(frame, detections: List[DetectedSign], detector: SignDetector):
    """Vẽ bounding box + nhãn (tên:confidence) trực tiếp lên frame truyền vào, trả về chính frame đó."""
    for det in detections:
        x1, y1, x2, y2 = det.bbox
        color = _box_color(det.sign_type, detector)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"{det.sign_type} {det.confidence:.2f}"
        cv2.putText(frame, label, (x1, max(0, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def extract_and_detect(
    video_path: str,
    detector: SignDetector,
    output_dir: str,
    interval_sec: float,
    limit: Optional[int],
) -> None:
    """
    Trích frame theo chu kỳ interval_sec giây từ video, chạy detect trên từng
    frame trích ra, lưu ảnh gốc + ảnh đã vẽ box, và 1 file JSON tổng hợp kết
    quả detect của tất cả frame.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Không mở được video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, int(round(fps * interval_sec)))
    os.makedirs(output_dir, exist_ok=True)

    results: Dict[str, List[dict]] = {}
    frame_index = 0
    saved_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % frame_interval == 0:
            detections = detector.detect(frame)
            timestamp_sec = frame_index / fps
            name = f"frame_{frame_index:06d}_t{timestamp_sec:.1f}s"

            cv2.imwrite(os.path.join(output_dir, f"{name}.jpg"), frame)
            annotated = draw_detections(frame.copy(), detections, detector)
            cv2.imwrite(os.path.join(output_dir, f"{name}_det.jpg"), annotated)

            results[name] = [d.to_dict() for d in detections]
            saved_count += 1
            logger.info(f"[{name}] {len(detections)} detection(s)")

            if limit is not None and saved_count >= limit:
                break

        frame_index += 1

    cap.release()

    summary_path = os.path.join(output_dir, "_detections.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Đã trích {saved_count} frame vào: {output_dir} (tổng hợp: {summary_path})")


def run_realtime(
    video_path: str,
    detector: SignDetector,
    save_video_path: Optional[str],
    save_json_path: Optional[str],
    process_every_n: int,
) -> None:
    """
    Phát video và detect theo thời gian thực - thực chất là đọc file video
    tuần tự và hiển thị kết quả ngay khi xử lý xong từng frame (không đợi xử
    lý xong toàn bộ video), không phải đọc từ camera sống.

    process_every_n: chỉ chạy detect mỗi N frame (các frame ở giữa dùng lại
    kết quả detect gần nhất để vẽ) - dùng khi video FPS cao hoặc máy chạy CPU
    chậm hơn tốc độ phát video.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Không mở được video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if save_video_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(save_video_path, fourcc, fps, (width, height))

    all_results: Dict[str, List[dict]] = {}
    last_detections: List[DetectedSign] = []
    frame_index = 0

    logger.info("Nhấn 'q' hoặc ESC trong cửa sổ preview để dừng.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % process_every_n == 0:
            last_detections = detector.detect(frame)
            if save_json_path:
                timestamp_sec = frame_index / fps
                all_results[f"frame_{frame_index:06d}_t{timestamp_sec:.1f}s"] = [
                    d.to_dict() for d in last_detections
                ]

        annotated = draw_detections(frame.copy(), last_detections, detector)

        if writer is not None:
            writer.write(annotated)

        cv2.imshow("Sign/Light Detection - nhan q de thoat", annotated)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break

        frame_index += 1

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()

    if save_json_path:
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Đã lưu kết quả detect ra: {save_json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trích frame / detect biển báo-đèn giao thông từ video hành trình")
    parser.add_argument("--video", type=str, required=True, help="Đường dẫn file video (.mp4, .MOV, ...)")
    parser.add_argument("--conf", type=float, default=None, help="Ghi đè confidence_threshold (mặc định lấy từ config.yaml)")

    parser.add_argument("--extract-frames", action="store_true", help="Trích frame theo chu kỳ + detect, lưu ra ảnh/JSON")
    parser.add_argument("--interval-sec", type=float, default=1.0, help="Chu kỳ trích frame (giây), dùng với --extract-frames")
    parser.add_argument("--output-dir", type=str, default=None, help="Thư mục lưu frame trích ra (mặc định: <tên_video>_frames)")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số frame trích ra (mặc định: hết video)")

    parser.add_argument("--realtime", action="store_true", help="Phát video + detect, hiển thị cửa sổ preview")
    parser.add_argument("--process-every-n", type=int, default=1, help="Chỉ chạy detect mỗi N frame khi --realtime (đỡ chậm)")
    parser.add_argument("--save-video", type=str, default=None, help="Lưu video đã vẽ box ra file (dùng với --realtime)")
    parser.add_argument("--save-json", type=str, default=None, help="Lưu kết quả detect từng frame ra JSON (dùng với --realtime)")

    args = parser.parse_args()

    setup_logging()

    if not args.extract_frames and not args.realtime:
        parser.error("Phải chọn --extract-frames hoặc --realtime (hoặc cả hai)")

    detector = build_sign_detector(args.conf)
    logger.info(f"Đã load SignDetector, confidence_threshold={detector.confidence_threshold}")

    if args.extract_frames:
        output_dir = args.output_dir or (os.path.splitext(os.path.basename(args.video))[0] + "_frames")
        extract_and_detect(args.video, detector, output_dir, args.interval_sec, args.limit)

    if args.realtime:
        run_realtime(args.video, detector, args.save_video, args.save_json, max(1, args.process_every_n))


if __name__ == "__main__":
    main()
