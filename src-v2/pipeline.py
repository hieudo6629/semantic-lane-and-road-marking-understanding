"""
Pipeline chính: nối perception (lane + sign detector) với analysis/reasoning
thành một luồng duy nhất, từ ảnh dashcam tới TrafficScene + prompt LLM.

    Ảnh dashcam
      -> perception.lane_detector.LaneDetector.detect()      -> lanes
      -> perception.sign_detector.SignDetector.detect()      -> detected_signs
      -> analysis.scene_builder.SceneBuilder.build()          -> TrafficScene
      -> reasoning.prompt_builder.PromptBuilder.build_scene_prompt() -> prompt cho LLM

Đây là điểm khác biệt cốt lõi so với `src/main.py` cũ: lane và sign LUÔN được
detect trên CÙNG MỘT ảnh trong CÙNG MỘT lần gọi process() - không còn khả năng
lấy lane thật ghép với sign thật nhưng lane GIẢ như main.py cũ (--signs dùng
demo_lane_reasoning hardcode, xem Phần 1 của bản phân tích).
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from analysis.scene_builder import SceneBuilder, TrafficScene
from perception.lane_detector import LaneDetector
from perception.sign_detector import SignDetector
from reasoning.prompt_builder import PromptBuilder, PromptStrategy
from utils.logger import get_logger
from utils.preprocessing import validate_image
from utils.visualization import visualize_scene

logger = get_logger(__name__)


@dataclass
class PipelineConfig:
    """Toàn bộ tham số cần để khởi tạo pipeline - thường load từ configs/config.yaml."""

    lane_model_path: str
    ufld_repo_path: str
    sign_model_path: str
    device: str = "cpu"
    is_urban: bool = True
    sign_confidence_threshold: float = 0.5


class TrafficScenePipeline:
    """Điều phối toàn bộ pipeline: ảnh -> perception -> analysis -> reasoning."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        logger.info("Đang khởi tạo pipeline (có thể mất vài giây để load model)...")

        self.lane_detector = LaneDetector(
            model_path=config.lane_model_path,
            ufld_repo_path=config.ufld_repo_path,
            device=config.device,
        )
        self.sign_detector = SignDetector(
            model_path=config.sign_model_path,
            confidence_threshold=config.sign_confidence_threshold,
            device=config.device,
        )
        self.scene_builder = SceneBuilder(is_urban=config.is_urban)
        self.prompt_builder = PromptBuilder()

        logger.info("Pipeline sẵn sàng.")

    def process(self, image: np.ndarray, current_speed: Optional[int] = None) -> TrafficScene:
        """
        Chạy toàn bộ pipeline trên MỘT ảnh, trả về TrafficScene (không kèm ảnh visualize).

        Args:
            image: ảnh BGR (kết quả cv2.imread).
            current_speed: tốc độ xe hiện tại (km/h), nếu có nguồn dữ liệu ngoài (OBD/GPS).
        """
        validation = validate_image(image)
        if not validation.is_valid:
            logger.warning(f"Ảnh đầu vào không hợp lệ: {validation.issues}")

        lanes = self.lane_detector.detect(image)
        detected_signs = self.sign_detector.detect(image, image.shape[1], image.shape[0])

        scene = self.scene_builder.build(
            lanes,
            image.shape[1],
            image.shape[0],
            detected_signs=detected_signs,
            current_speed=current_speed,
        )
        return scene

    def process_and_visualize(
        self, image: np.ndarray, current_speed: Optional[int] = None
    ) -> Tuple[TrafficScene, np.ndarray]:
        """Giống process(), nhưng trả kèm ảnh đã vẽ overlay (lane + corridor + sign)."""
        validation = validate_image(image)
        if not validation.is_valid:
            logger.warning(f"Ảnh đầu vào không hợp lệ: {validation.issues}")

        lanes = self.lane_detector.detect(image)
        detected_signs = self.sign_detector.detect(image, image.shape[1], image.shape[0])

        scene = self.scene_builder.build(
            lanes,
            image.shape[1],
            image.shape[0],
            detected_signs=detected_signs,
            current_speed=current_speed,
        )
        vis = visualize_scene(image, lanes, scene.lane, detected_signs=detected_signs)
        return scene, vis

    def build_prompt(self, scene: TrafficScene, strategy: PromptStrategy = PromptStrategy.ZERO_SHOT) -> str:
        """Sinh prompt LLM (Phi-3-mini) từ một TrafficScene đã build."""
        self.prompt_builder.config.strategy = strategy
        return self.prompt_builder.build_scene_prompt(scene)

    def self_test(self) -> dict:
        """
        Kiểm tra nhanh cả 2 model (lane + sign) có load/chạy được không, KHÔNG
        cần ảnh thật - dùng để xác định lỗi đến từ model/môi trường hay từ dữ
        liệu ảnh đầu vào cụ thể (yêu cầu mục D.2 của dự án).
        """
        return {
            "lane_detector": self.lane_detector.self_test(),
            "sign_detector": self.sign_detector.self_test(),
        }
