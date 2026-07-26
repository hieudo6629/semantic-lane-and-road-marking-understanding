"""
Chạy pipeline hàng loạt trên toàn bộ ảnh trong một thư mục input, lưu ảnh
visualize + JSON scene tương ứng cho từng ảnh vào thư mục output.

Cách dùng:
    python batch_process.py --input path/to/input_dir --output path/to/output_dir
    python batch_process.py --input in/ --output out/ --speed 60 --limit 50

Với mỗi ảnh "ten_anh.jpg" trong thư mục input, script tạo ra trong thư mục output:
    - ten_anh.json   : TrafficScene đầy đủ (dạng JSON, xem analysis/scene_builder.py)
    - ten_anh_vis.jpg: ảnh gốc có vẽ overlay lane/corridor/sign

Ảnh lỗi (không đọc được, hoặc pipeline lỗi giữa chừng) sẽ được LOG lại và
BỎ QUA, không làm dừng cả batch - kết quả tổng hợp in ra cuối cùng và lưu
vào output/_summary.json để xem lại.
"""

import argparse
import json
import os
import time
from typing import List

import cv2

from main import build_pipeline_config, load_raw_config
from pipeline import TrafficScenePipeline
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


def find_images(input_dir: str) -> List[str]:
    """Liệt kê toàn bộ file ảnh trong input_dir (không đệ quy vào thư mục con)."""
    names = sorted(os.listdir(input_dir))
    return [
        os.path.join(input_dir, name)
        for name in names
        if name.lower().endswith(IMAGE_EXTENSIONS)
    ]


def process_one_image(pipeline: TrafficScenePipeline, image_path: str, output_dir: str, speed: int) -> dict:
    """
    Xử lý 1 ảnh, lưu kết quả, trả về dict thống kê (dùng để tổng hợp summary).
    Raise exception nếu lỗi - để hàm gọi (run_batch) quyết định log và bỏ qua.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không đọc được ảnh (file hỏng hoặc không đúng định dạng): {image_path}")

    start = time.time()
    scene, vis = pipeline.process_and_visualize(image, current_speed=speed)
    elapsed = time.time() - start

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f"{base_name}.json")
    vis_path = os.path.join(output_dir, f"{base_name}_vis.jpg")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scene.to_dict(), f, indent=2, ensure_ascii=False)
    cv2.imwrite(vis_path, vis)

    return {
        "image": os.path.basename(image_path),
        "lane_count": len(scene.lane.sorted_lanes),
        "road_type": scene.road.road_type,
        "signs_detected": len(scene.detected_signs),
        "recommendation": scene.recommendation.action if scene.recommendation else None,
        "elapsed_seconds": round(elapsed, 3),
    }


def run_batch(pipeline: TrafficScenePipeline, input_dir: str, output_dir: str, speed: int, limit: int) -> None:
    os.makedirs(output_dir, exist_ok=True)

    image_paths = find_images(input_dir)
    if limit is not None:
        image_paths = image_paths[:limit]

    if not image_paths:
        logger.error(f"Không tìm thấy ảnh nào ({IMAGE_EXTENSIONS}) trong: {input_dir}")
        return

    logger.info(f"Tìm thấy {len(image_paths)} ảnh trong {input_dir}. Bắt đầu xử lý...")

    results = []
    failures = []
    batch_start = time.time()

    for i, image_path in enumerate(image_paths, start=1):
        try:
            stats = process_one_image(pipeline, image_path, output_dir, speed)
            results.append(stats)
            logger.info(
                f"[{i}/{len(image_paths)}] OK  {stats['image']}: "
                f"{stats['lane_count']} lanes, road={stats['road_type']}, "
                f"signs={stats['signs_detected']}, action={stats['recommendation']} "
                f"({stats['elapsed_seconds']}s)"
            )
        except Exception as exc:  # noqa: BLE001 - lỗi 1 ảnh không được làm dừng cả batch
            logger.error(f"[{i}/{len(image_paths)}] LỖI {os.path.basename(image_path)}: {exc}")
            failures.append({"image": os.path.basename(image_path), "error": str(exc)})

    total_elapsed = time.time() - batch_start
    summary = {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_images": len(image_paths),
        "succeeded": len(results),
        "failed": len(failures),
        "total_elapsed_seconds": round(total_elapsed, 2),
        "avg_seconds_per_image": round(total_elapsed / len(image_paths), 3) if image_paths else 0,
        "results": results,
        "failures": failures,
    }

    summary_path = os.path.join(output_dir, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(
        f"HOÀN TẤT: {summary['succeeded']}/{summary['total_images']} ảnh thành công, "
        f"{summary['failed']} lỗi, tổng {summary['total_elapsed_seconds']}s. "
        f"Xem chi tiết tại: {summary_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Chạy pipeline hàng loạt trên một thư mục ảnh")
    parser.add_argument("--input", type=str, required=True, help="Thư mục chứa ảnh đầu vào")
    parser.add_argument("--output", type=str, required=True, help="Thư mục lưu ảnh visualize + JSON")
    parser.add_argument("--speed", type=int, default=None, help="Tốc độ xe hiện tại (km/h), áp dụng cho mọi ảnh")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số ảnh xử lý (hữu ích khi test nhanh)")
    args = parser.parse_args()

    raw_config = load_raw_config()
    setup_logging(log_file=raw_config.get("logging", {}).get("log_file"))

    if not os.path.isdir(args.input):
        logger.error(f"Thư mục input không tồn tại: {args.input}")
        return

    pipeline_config = build_pipeline_config(raw_config)
    pipeline = TrafficScenePipeline(pipeline_config)

    run_batch(pipeline, args.input, args.output, args.speed, args.limit)


if __name__ == "__main__":
    main()
