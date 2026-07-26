"""
Gộp toàn bộ kết quả phân tích (làn đường + biển báo) thành một JSON scene
duy nhất, sẵn sàng cho reasoning/prompt_builder.py và LLM.

Refactor + gộp từ:
- src/semantic_scene.py   -> SemanticSceneBuilder (chỉ có thông tin làn đường)
- src/integrated_scene.py -> IntegratedSceneBuilder (làn đường + biển báo)

Hai file cũ thực chất làm CÙNG MỘT VIỆC (build scene JSON) nhưng độc lập
với nhau: semantic_scene.py là bản "chỉ có lane" được main.py dùng thật,
còn integrated_scene.py là bản "lane + sign" nhưng chỉ được gọi với dữ liệu
lane GIẢ LẬP hard-code trong main.py --signs (xem Phần 1 của phân tích) -
đây chính là lý do output biển báo/gợi ý lái xe trước đây không phản ánh
đúng làn đường thật. SceneBuilder ở đây thay thế cả 2, luôn dùng chung một
kết quả LaneAnalyzer thật cho cả hai loại thông tin.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from analysis.lane_analyzer import Lane, LaneAnalysisResult, LaneAnalyzer
from analysis.road_type import RoadTypeAnalyzer, RoadTypeResult
from perception.sign_detector import DetectedSign
from reasoning.recommendation import (
    Recommendation,
    RecommendationEngine,
    SignRuleInterpreter,
    TrafficSituation,
)
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrafficScene:
    """Đại diện đầy đủ cho một khung hình: làn đường + biển báo + gợi ý lái xe."""

    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    image_width: int = 0
    image_height: int = 0

    lane: LaneAnalysisResult = field(default_factory=LaneAnalysisResult)
    road: RoadTypeResult = field(default_factory=RoadTypeResult)
    detected_signs: List[DetectedSign] = field(default_factory=list)
    traffic_situation: TrafficSituation = field(default_factory=TrafficSituation)
    recommendation: Optional[Recommendation] = None

    def to_dict(self) -> Dict:
        """Chuyển thành dict thuần Python/JSON-serializable - schema dùng chung cho toàn pipeline."""
        return {
            "scene_id": self.scene_id,
            "timestamp": self.timestamp,
            "image_size": {"width": self.image_width, "height": self.image_height},
            "road": self.road.to_dict(),
            "lane": self.lane.to_dict(),
            "traffic_signs": {
                "detected": [s.to_dict() for s in self.detected_signs],
                "count": len(self.detected_signs),
            },
            "traffic_situation": self.traffic_situation.to_dict(),
            "recommendation": self.recommendation.to_dict() if self.recommendation else None,
        }


class SceneBuilder:
    """
    Điều phối toàn bộ bước phân tích: lane -> road type -> diễn giải biển báo
    -> gợi ý lái xe, rồi gộp thành một TrafficScene duy nhất.

    Đây là điểm nối chính giữa 2 nhánh trước đây bị tách rời (xem docstring
    đầu file): mọi lời gọi build() đều dùng CÙNG MỘT danh sách `lanes` phát
    hiện được trên CÙNG MỘT ảnh để vừa phân tích làn đường vừa diễn giải biển
    báo - không còn khả năng lane và sign đến từ 2 nguồn dữ liệu khác nhau.
    """

    def __init__(self, is_urban: bool = True):
        self.lane_analyzer = LaneAnalyzer()
        self.road_type_analyzer = RoadTypeAnalyzer()
        self.sign_interpreter = SignRuleInterpreter(is_urban=is_urban)
        self.recommendation_engine = RecommendationEngine()

    def build(
        self,
        lanes: List[Lane],
        image_width: int,
        image_height: int,
        detected_signs: Optional[List[DetectedSign]] = None,
        current_speed: Optional[int] = None,
    ) -> TrafficScene:
        """
        Args:
            lanes: làn đường phát hiện được trên ảnh (từ perception.lane_detector).
            image_width, image_height: kích thước ảnh gốc.
            detected_signs: biển báo phát hiện được TRÊN CÙNG ẢNH (từ
                            perception.sign_detector) - có thể để trống nếu
                            chưa chạy sign detector.
            current_speed: tốc độ xe hiện tại (km/h), nếu có nguồn dữ liệu
                            (ví dụ OBD/GPS) - dùng để tính gợi ý tốc độ chính xác hơn.

        Returns:
            TrafficScene hoàn chỉnh.
        """
        lane_result = self.lane_analyzer.analyze(lanes, image_width, image_height)
        road_result = self.road_type_analyzer.infer(
            lanes, lane_result.ego_lane, lane_result.aggregated_curvature, image_width, image_height
        )

        detected_signs = detected_signs or []
        traffic_situation = self.sign_interpreter.interpret(detected_signs, current_speed)

        scene = TrafficScene(
            image_width=image_width,
            image_height=image_height,
            lane=lane_result,
            road=road_result,
            detected_signs=detected_signs,
            traffic_situation=traffic_situation,
        )
        scene.recommendation = self.recommendation_engine.generate(scene)

        logger.info(
            f"Scene {scene.scene_id[:8]}: road={road_result.road_type}, "
            f"ego_lane_confidence={lane_result.ego_lane.confidence:.2f}, "
            f"signs={len(detected_signs)}, action={scene.recommendation.action}"
        )
        return scene


def build_scene(
    lanes: List[Lane],
    image_width: int,
    image_height: int,
    detected_signs: Optional[List[DetectedSign]] = None,
    current_speed: Optional[int] = None,
    is_urban: bool = True,
) -> TrafficScene:
    """Hàm tiện ích: tạo SceneBuilder mặc định và build ngay."""
    return SceneBuilder(is_urban=is_urban).build(
        lanes, image_width, image_height, detected_signs=detected_signs, current_speed=current_speed
    )
