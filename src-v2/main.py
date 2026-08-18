"""
Entry point CLI cho pipeline Semantic Traffic Scene Understanding.

Cách dùng:
    python main.py --image path/to/anh.jpg [--speed 60] [--save-vis out.jpg]
    python main.py --culane [--index 45]
    python main.py --demo
    python main.py --self-test

Xem configs/config.yaml để chỉnh đường dẫn model, ngưỡng confidence, v.v.
"""

import argparse
import glob
import json
import logging
import os

import cv2
import yaml

from pipeline import PipelineConfig, TrafficScenePipeline
from reasoning.prompt_builder import PromptBuilder, PromptStrategy, SceneDescriber
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs", "config.yaml")


def load_raw_config() -> dict:
    """Đọc trực tiếp configs/config.yaml thành dict."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_path(path: str) -> str:
    """Chuyển đường dẫn tương đối trong config.yaml thành tuyệt đối, tính từ vị trí file config."""
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(os.path.dirname(CONFIG_PATH), path))


def build_pipeline_config(raw: dict) -> PipelineConfig:
    """Chuyển dict đọc từ YAML thành PipelineConfig có kiểu rõ ràng."""
    models = raw.get("models", {})
    return PipelineConfig(
        lane_model_path=_resolve_path(models["lane_model_path"]),
        ufld_repo_path=_resolve_path(models["ufld_repo_path"]),
        sign_model_path=_resolve_path(models["sign_model_path"]),
        device=models.get("device", "cpu"),
        is_urban=raw.get("scene", {}).get("is_urban", True),
        sign_confidence_threshold=raw.get("sign_detection", {}).get("confidence_threshold", 0.5),
        lane_dataset=models.get("lane_dataset", "culane"),
        lane_backbone=str(models.get("lane_backbone", "34")),
    )


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def run_on_image(pipeline: TrafficScenePipeline, image_path: str, speed: int, save_vis_path: str) -> None:
    """Chạy toàn bộ pipeline trên một file ảnh cụ thể và in kết quả ra console."""
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Không đọc được ảnh (kiểm tra lại đường dẫn): {image_path}")
        return

    scene, vis = pipeline.process_and_visualize(image, current_speed=speed)

    print("\n=== SEMANTIC SCENE (JSON) ===")
    _print_json(scene.to_dict())

    print("\n=== MÔ TẢ TỰ NHIÊN ===")
    print(SceneDescriber().generate_full(scene))

    print("\n=== PROMPT CHO LLM (Phi-3-mini) ===")
    print(pipeline.build_prompt(scene, PromptStrategy.ZERO_SHOT))

    if save_vis_path:
        cv2.imwrite(save_vis_path, vis)
        logger.info(f"Đã lưu ảnh visualize tại: {save_vis_path}")


def run_on_culane_sample(
    pipeline: TrafficScenePipeline, culane_root: str, index: int, speed: int = None, save_vis_path: str = None
) -> None:
    """
    Lấy 1 ảnh thật từ dataset CULane theo index rồi chạy pipeline đầy đủ (bao
    gồm cả lane_detector.py thật) - KHÔNG dùng nhãn .lines.txt có sẵn, vì mục
    đích là kiểm tra model tự detect trên ảnh thật, không phải đọc nhãn.
    """
    if not culane_root or not os.path.isdir(culane_root):
        logger.error(f"Không tìm thấy thư mục dataset CULane: {culane_root}")
        return

    image_paths = sorted(glob.glob(os.path.join(culane_root, "**", "*.jpg"), recursive=True))
    if not image_paths:
        logger.error(f"Không tìm thấy ảnh .jpg nào trong: {culane_root}")
        return

    index = index % len(image_paths)
    image_path = image_paths[index]
    logger.info(f"Dataset CULane có {len(image_paths)} ảnh - dùng ảnh index {index}: {image_path}")
    run_on_image(pipeline, image_path, speed, save_vis_path)


def run_demo() -> None:
    """
    Chạy phần analysis/reasoning bằng dữ liệu làn MẪU (không phải từ model
    thật) - KHÔNG cần load lane_detector/sign_detector, hữu ích để kiểm tra
    nhanh logic phân tích/reasoning trên máy không có GPU hoặc chưa có file
    model.
    """
    from analysis.scene_builder import build_scene

    example_lanes = [
        [(-16.44, 580), (22.27, 570), (50.12, 560), (100.35, 540), (180.55, 510),
         (280.42, 470), (400.15, 420), (520.33, 380), (620.50, 350), (681.38, 400)],
        [(533.50, 590), (542.95, 580), (562.30, 560), (592.15, 530), (642.30, 490),
         (712.25, 440), (762.85, 390), (733.45, 400)],
        [(1186.93, 590), (1166.92, 580), (1106.50, 550), (1020.30, 510), (920.15, 460),
         (850.45, 410), (773.33, 400)],
        [(1668.99, 550), (1613.13, 540), (1520.50, 500), (1400.25, 450), (1280.40, 400),
         (1150.60, 360), (825.60, 400)],
    ]

    scene = build_scene(example_lanes, image_width=1640, image_height=590, current_speed=70)

    print("\n=== SEMANTIC SCENE (JSON) ===")
    _print_json(scene.to_dict())

    print("\n=== MÔ TẢ TỰ NHIÊN ===")
    print(SceneDescriber().generate_full(scene))

    print("\n=== PROMPT CHO LLM (Phi-3-mini) ===")
    print(PromptBuilder().build_scene_prompt(scene))


def run_self_test(pipeline: TrafficScenePipeline) -> None:
    """In kết quả self-test của cả 2 model (lane + sign) - dùng để chẩn đoán lỗi model vs. lỗi ảnh đầu vào."""
    _print_json(pipeline.self_test())


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic Traffic Scene Understanding Pipeline")
    parser.add_argument("--image", type=str, help="Đường dẫn ảnh dashcam để chạy pipeline")
    parser.add_argument("--speed", type=int, default=None, help="Tốc độ xe hiện tại (km/h), nếu biết")
    parser.add_argument("--save-vis", type=str, default=None, help="Đường dẫn lưu ảnh visualize (overlay lane+sign)")
    parser.add_argument("--culane", action="store_true", help="Chạy trên 1 ảnh mẫu từ dataset CULane (xem configs/config.yaml)")
    parser.add_argument("--index", type=int, default=45, help="Index ảnh trong dataset CULane (dùng với --culane)")
    parser.add_argument("--demo", action="store_true", help="Chạy demo bằng dữ liệu làn mẫu, không cần load model")
    parser.add_argument("--self-test", action="store_true", help="Kiểm tra model/preprocessing có hoạt động không")
    args = parser.parse_args()

    raw_config = load_raw_config()
    log_cfg = raw_config.get("logging", {})
    setup_logging(
        level=getattr(logging, str(log_cfg.get("level", "INFO")).upper(), logging.INFO),
        log_file=log_cfg.get("log_file"),
    )

    if args.demo:
        run_demo()
        return

    pipeline_config = build_pipeline_config(raw_config)
    pipeline = TrafficScenePipeline(pipeline_config)

    if args.self_test:
        run_self_test(pipeline)
    elif args.image:
        run_on_image(pipeline, args.image, args.speed, args.save_vis)
    elif args.culane:
        culane_root = raw_config.get("datasets", {}).get("culane_root")
        run_on_culane_sample(pipeline, culane_root, args.index, args.speed, args.save_vis)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
