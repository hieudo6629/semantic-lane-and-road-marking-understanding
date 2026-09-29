"""
Chạy pipeline hàng loạt trên toàn bộ ảnh trong một thư mục input, lưu ảnh
visualize + JSON scene tương ứng cho từng ảnh vào thư mục output.

Cách dùng:
    python batch_process.py --input path/to/input_dir --output path/to/output_dir
    python batch_process.py --input in/ --output out/ --speed 60 --limit 50

Với mỗi ảnh "ten_anh.jpg" trong thư mục input, script tạo ra trong thư mục output:
    - ten_anh.json       : TrafficScene đầy đủ (dạng JSON thô, xem analysis/scene_builder.py) -
                           KHÔNG gồm "traffic_situation"/"recommendation" (đã bỏ, xem
                           process_one_image() - tập trung vào làn đường, không dùng
                           tới suy luận biển báo/khuyến nghị đơn giản if-else)
    - ten_anh_brief.json : bản RÚT GỌN từ JSON thô, chỉ giữ thông tin chính về
                           làn đường (số làn, vị trí ego lane, độ lệch tâm, số
                           làn trái/phải, hình dạng đường) - xem analysis/scene_summarizer.py
    - ten_anh_vis.jpg    : ảnh gốc có vẽ overlay lane/corridor/sign

Ảnh lỗi (không đọc được, hoặc pipeline lỗi giữa chừng) sẽ được LOG lại và
BỎ QUA, không làm dừng cả batch - kết quả tổng hợp in ra cuối cùng và lưu
vào output/_summary.json để xem lại.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import cv2

from analysis.scene_summarizer import summarize_scene
from main import build_pipeline_config, load_raw_config
from perception.sign_detector import _load_sign_mapping
from pipeline import TrafficScenePipeline
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")

TIMING_LOG_FILENAME = "_extraction_timings.json"

SIGN_MAPPING = _load_sign_mapping()


def build_brief(scene_dict: Dict) -> Dict:
    """summarize_scene() + định dạng lại traffic_signs.detected thành
    {sign_code, confidence, bbox, relative_position, sign_name, sign_type}
    (sign_name/sign_type tra từ configs/traffic_sign_mapping.json theo mã gốc)."""
    brief = summarize_scene(scene_dict)
    detected = []
    for sign in scene_dict.get("traffic_signs", {}).get("detected", []):
        code = sign.get("raw_class_name")
        info = SIGN_MAPPING.get(code, {})
        detected.append({
            "sign_code": code,
            "confidence": round(sign.get("confidence", 0.0), 2),
            "bbox": sign.get("bbox"),
            "relative_position": sign.get("relative_position"),
            "sign_name": info.get("name", sign.get("display_name") or code),
            "sign_type": info.get("type"),
        })
    brief["traffic_signs"] = {"detected": detected, "count": len(detected)}
    return brief


def rebuild_briefs(output_dir: str) -> None:
    """Tạo lại toàn bộ <ten>_brief.json từ <ten>.json đã có, không chạy lại pipeline."""
    names = sorted(
        n for n in os.listdir(output_dir)
        if n.endswith(".json") and not n.endswith("_brief.json") and not n.startswith("_")
    )
    for name in names:
        with open(os.path.join(output_dir, name), "r", encoding="utf-8") as f:
            scene_dict = json.load(f)
        brief_path = os.path.join(output_dir, f"{os.path.splitext(name)[0]}_brief.json")
        with open(brief_path, "w", encoding="utf-8") as f:
            json.dump(build_brief(scene_dict), f, indent=2, ensure_ascii=False)
    logger.info(f"Đã tạo lại {len(names)} file brief trong {output_dir}.")


def load_timing_log(output_dir: str) -> Dict[str, Dict]:
    """Đọc file log thời gian xử lý từng ảnh đã có (nếu có) trong output_dir."""
    path = os.path.join(output_dir, TIMING_LOG_FILENAME)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_timing_log(output_dir: str, timing_log: Dict[str, Dict]) -> None:
    path = os.path.join(output_dir, TIMING_LOG_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(timing_log, f, indent=2, ensure_ascii=False, sort_keys=True)


def find_images(input_dir: str) -> List[str]:
    """Liệt kê toàn bộ file ảnh trong input_dir (không đệ quy vào thư mục con).

    Bỏ qua ảnh "<số>_observed.jpg" (ảnh quan sát/tham chiếu đi kèm mỗi ảnh gốc
    trong input/, không phải ảnh cần chạy pipeline) - chỉ xử lý "<số>.jpg".
    """
    names = sorted(os.listdir(input_dir))
    return [
        os.path.join(input_dir, name)
        for name in names
        if name.lower().endswith(IMAGE_EXTENSIONS)
        and not os.path.splitext(name)[0].lower().endswith("_observed")
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
    brief_path = os.path.join(output_dir, f"{base_name}_brief.json")
    vis_path = os.path.join(output_dir, f"{base_name}_vis.jpg")

    scene_dict = scene.to_dict()
    # Bỏ traffic_situation/recommendation khỏi JSON lưu ra - phạm vi hiện tại
    # chỉ tập trung vào làn đường, không dùng tới suy luận biển báo/khuyến
    # nghị đơn giản if-else (xem reasoning/recommendation.py) - 2 trường này
    # vẫn được TrafficScenePipeline tính (không sửa scene_builder.py, giữ
    # nguyên cho các nơi gọi khác như main.py), chỉ không ghi ra file ở đây.
    scene_dict.pop("traffic_situation", None)
    scene_dict.pop("recommendation", None)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scene_dict, f, indent=2, ensure_ascii=False)
    with open(brief_path, "w", encoding="utf-8") as f:
        json.dump(build_brief(scene_dict), f, indent=2, ensure_ascii=False)
    cv2.imwrite(vis_path, vis)

    return {
        "image": os.path.basename(image_path),
        "lane_count": len(scene.lane.sorted_lanes),
        "road_type": scene.road.road_type,
        "signs_detected": len(scene.detected_signs),
        "elapsed_seconds": round(elapsed, 3),
    }


def run_batch(
    pipeline: TrafficScenePipeline,
    input_dir: str,
    output_dir: str,
    speed: int,
    limit: int,
    stems: Optional[List[str]] = None,
    overwrite: bool = False,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    image_paths = find_images(input_dir)
    if not overwrite:
        before = len(image_paths)
        image_paths = [
            p for p in image_paths
            if not os.path.exists(os.path.join(output_dir, f"{os.path.splitext(os.path.basename(p))[0]}.json"))
        ]
        skipped = before - len(image_paths)
        if skipped:
            logger.info(f"Bỏ qua {skipped} ảnh đã có kết quả trong {output_dir} (dùng --overwrite để ghi đè).")
    if stems:
        wanted = set(stems)
        image_paths = [p for p in image_paths if os.path.splitext(os.path.basename(p))[0] in wanted]
        missing = wanted - {os.path.splitext(os.path.basename(p))[0] for p in image_paths}
        if missing:
            logger.warning(f"{len(missing)} stem trong --stems không tìm thấy ảnh tương ứng, bỏ qua: {sorted(missing)}")
    if limit is not None:
        image_paths = image_paths[:limit]

    if not image_paths:
        logger.error(f"Không tìm thấy ảnh nào ({IMAGE_EXTENSIONS}) trong: {input_dir}")
        return

    logger.info(f"Tìm thấy {len(image_paths)} ảnh trong {input_dir}. Bắt đầu xử lý...")

    # File log thời gian xử lý, 1 entry/ảnh (theo tên không phần mở rộng) -
    # khi chạy lại đúng ảnh đó (VD qua --stems), entry cũ bị GHI ĐÈ bằng lần
    # đo mới nhất, các ảnh khác trong log không bị ảnh hưởng.
    timing_log = load_timing_log(output_dir)

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
                f"signs={stats['signs_detected']} "
                f"({stats['elapsed_seconds']}s)"
            )

            base_name = os.path.splitext(os.path.basename(image_path))[0]
            timing_log[base_name] = {
                "elapsed_seconds": stats["elapsed_seconds"],
                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            save_timing_log(output_dir, timing_log)
        except Exception as exc:  # noqa: BLE001 - lỗi 1 ảnh không được làm dừng cả batch
            logger.error(f"[{i}/{len(image_paths)}] LỖI {os.path.basename(image_path)}: {exc}")
            failures.append({"image": os.path.basename(image_path), "error": str(exc)})

    total_elapsed = time.time() - batch_start

    all_times = [entry["elapsed_seconds"] for entry in timing_log.values()]
    summary = {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_images": len(image_paths),
        "succeeded": len(results),
        "failed": len(failures),
        "total_elapsed_seconds": round(total_elapsed, 2),
        "avg_seconds_per_image": round(total_elapsed / len(image_paths), 3) if image_paths else 0,
        "num_images_logged": len(all_times),
        "total_elapsed_seconds_logged": round(sum(all_times), 2),
        "avg_seconds_per_image_logged": round(sum(all_times) / len(all_times), 3) if all_times else 0,
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
    parser.add_argument("--input", type=str, default=None, help="Thư mục chứa ảnh đầu vào")
    parser.add_argument("--output", type=str, required=True, help="Thư mục lưu ảnh visualize + JSON")
    parser.add_argument("--speed", type=int, default=None, help="Tốc độ xe hiện tại (km/h), áp dụng cho mọi ảnh")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số ảnh xử lý (hữu ích khi test nhanh)")
    parser.add_argument(
        "--stems", type=str, default=None,
        help="Danh sách tên ảnh (không phần mở rộng), phân cách bởi dấu phẩy, để chỉ chạy lại đúng các ảnh đó, VD: --stems 179,42",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Ghi đè ảnh đã có kết quả trong output_dir. Mặc định (không truyền cờ này) sẽ bỏ qua các ảnh đã có file <ten>.json.",
    )
    parser.add_argument(
        "--rebrief", action="store_true",
        help="Chỉ tạo lại <ten>_brief.json từ các <ten>.json đã có trong --output, không chạy pipeline.",
    )
    args = parser.parse_args()

    raw_config = load_raw_config()
    setup_logging(log_file=raw_config.get("logging", {}).get("log_file"))

    if args.rebrief:
        rebuild_briefs(args.output)
        return

    if not args.input or not os.path.isdir(args.input):
        logger.error(f"Thư mục input không tồn tại: {args.input}")
        return

    pipeline_config = build_pipeline_config(raw_config)
    pipeline = TrafficScenePipeline(pipeline_config)

    stems = [s.strip() for s in args.stems.split(",") if s.strip()] if args.stems else None
    run_batch(pipeline, args.input, args.output, args.speed, args.limit, stems=stems, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
