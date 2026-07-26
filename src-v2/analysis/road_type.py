"""
Suy luận loại đường (road type) và môi trường đường (road environment).

Refactor từ src/road_type_inference.py.

BUG ĐÃ SỬA (quan trọng): bản cũ tự định nghĩa 2 ngưỡng
`CURVE_THRESHOLD_GENTLE = 2e-4` và `CURVE_THRESHOLD_SHARP = 5e-4` rồi so
sánh với `curvature_magnitude` lấy từ `lane_curvature.aggregate_curvature()`.
Nhưng hàm đó tự tính `curvature_magnitude` ở một thang giá trị hoàn toàn
khác (ví dụ đường thẳng cho ra ~0.01-0.05, đường cong nhẹ cho ra ~0.1-2) -
tức là LỚN HƠN ngưỡng "sharp" (0.0005) tới hàng trăm lần. Hậu quả: bất cứ
khi nào hướng cong (direction) không phải "straight", hệ thống gần như
LUÔN LUÔN phân loại nhầm thành "sharp_x_curve" kể cả với các khúc cua rất
nhẹ, vì ngưỡng so sánh sai đơn vị.

Cách sửa: không tính lại phân loại độ cong ở đây nữa. `LaneAnalyzer` (xem
analysis/lane_analyzer.py) đã tính `classification` (straight / gentle_x_curve /
sharp_x_curve) với ngưỡng ĐÚNG thang đo ngay tại nơi sinh ra magnitude đó.
road_type.py chỉ tái sử dụng kết quả này, tránh có 2 nơi tự phân loại độ
cong với 2 bộ ngưỡng không khớp nhau.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from analysis.lane_analyzer import AggregatedCurvature, EgoLaneInfo, Lane
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RoadGeometry:
    """Đặc điểm hình học của mặt đường quan sát được, dùng để suy ra môi trường đường."""
    spread_pixels: float = 0.0
    coverage_ratio: float = 0.0       # spread / image_width - đường càng "phủ" rộng ảnh càng nhiều làn
    convergence_ratio: float = 0.0    # spread_bottom / spread_top - đo mức hội tụ phối cảnh
    lane_count: int = 0
    geometry_type: str = "unknown"    # narrow | single_lane_view | multi_lane

    def to_dict(self) -> Dict:
        return {
            "spread_pixels": float(self.spread_pixels),
            "coverage_ratio": float(self.coverage_ratio),
            "convergence_ratio": float(self.convergence_ratio),
            "lane_count": self.lane_count,
            "geometry_type": self.geometry_type,
        }


@dataclass
class RoadTypeResult:
    road_type: str = "unknown"                # straight | gentle_left_curve | sharp_right_curve | ...
    road_environment: str = "unknown"          # narrow_road | urban_multi_lane | highway | rural_road | ...
    curvature_magnitude: float = 0.0
    curvature_direction: str = "unknown"
    curvature_confidence: float = 0.0
    geometry: RoadGeometry = field(default_factory=RoadGeometry)

    def to_dict(self) -> Dict:
        return {
            "road_type": self.road_type,
            "road_environment": self.road_environment,
            "curvature_magnitude": float(self.curvature_magnitude),
            "curvature_direction": self.curvature_direction,
            "curvature_confidence": float(self.curvature_confidence),
            "geometry": self.geometry.to_dict(),
        }


class RoadTypeAnalyzer:
    """Suy luận loại đường + môi trường đường từ hình học làn và độ cong đã tính sẵn."""

    def infer(
        self,
        lanes: List[Lane],
        ego_lane: EgoLaneInfo,
        aggregated_curvature: AggregatedCurvature,
        image_width: int,
        image_height: int,
    ) -> RoadTypeResult:
        """
        Args:
            lanes: danh sách làn gốc (điểm (x, y)).
            ego_lane: kết quả ego lane từ LaneAnalyzer (hiện chưa dùng trực tiếp,
                      giữ tham số để mở rộng sau, ví dụ suy luận môi trường theo
                      bề rộng ego lane thực tế).
            aggregated_curvature: kết quả độ cong đã tính bởi LaneAnalyzer -
                      TÁI SỬ DỤNG, không tính lại.
            image_width, image_height: kích thước ảnh gốc.
        """
        if not lanes:
            return RoadTypeResult()

        geometry = self._analyze_geometry(lanes, image_width, image_height)
        road_environment = self._infer_environment(geometry)

        return RoadTypeResult(
            road_type=aggregated_curvature.classification,
            road_environment=road_environment,
            curvature_magnitude=aggregated_curvature.curvature_magnitude,
            curvature_direction=aggregated_curvature.direction,
            curvature_confidence=aggregated_curvature.confidence,
            geometry=geometry,
        )

    def _analyze_geometry(self, lanes: List[Lane], image_width: int, image_height: int) -> RoadGeometry:
        """Đo độ trải rộng và mức hội tụ của các làn để suy ra kiểu hình học mặt đường."""
        y_bottom = int(image_height * 0.95)
        y_top = int(image_height * 0.3)

        x_bottom = self._x_positions_near_y(lanes, y_bottom)
        x_top = self._x_positions_near_y(lanes, y_top)

        if not x_bottom:
            return RoadGeometry(geometry_type="unknown", lane_count=len(lanes))

        spread_bottom = max(x_bottom) - min(x_bottom)
        coverage_ratio = spread_bottom / image_width if image_width > 0 else 0.0

        convergence_ratio = 0.0
        if len(x_bottom) >= 2 and len(x_top) >= 2:
            spread_top = max(x_top) - min(x_top)
            if spread_top > 0:
                convergence_ratio = spread_bottom / spread_top

        if coverage_ratio < 0.3:
            geometry_type = "narrow"
        elif coverage_ratio < 0.6:
            geometry_type = "single_lane_view"
        else:
            geometry_type = "multi_lane"

        return RoadGeometry(
            spread_pixels=float(spread_bottom),
            coverage_ratio=float(coverage_ratio),
            convergence_ratio=float(convergence_ratio),
            lane_count=len(lanes),
            geometry_type=geometry_type,
        )

    def _x_positions_near_y(self, lanes: List[Lane], y_target: int, tolerance: int = 50) -> List[float]:
        """Lấy tọa độ x trung bình của mỗi làn tại các điểm gần y_target."""
        positions = []
        for lane in lanes:
            nearby = [p[0] for p in lane if abs(p[1] - y_target) < tolerance]
            if nearby:
                positions.append(float(np.mean(nearby)))
        return positions

    def _infer_environment(self, geometry: RoadGeometry) -> str:
        """Suy luận môi trường đường (đô thị / cao tốc / nông thôn) từ số làn và độ phủ."""
        if geometry.geometry_type == "narrow":
            return "narrow_road"
        if geometry.lane_count >= 4 and geometry.coverage_ratio > 0.5:
            return "urban_marketplace"
        if geometry.lane_count >= 3:
            return "urban_multi_lane"
        if geometry.lane_count <= 2:
            return "highway" if geometry.coverage_ratio > 0.4 else "rural_road"
        return "urban_road"


# Mô tả tiếng Việt ngắn gọn cho từng loại road_type - dùng trong prompt_builder / debug log
ROAD_TYPE_DESCRIPTIONS_VI: Dict[str, str] = {
    "straight": "Đường phía trước gần như thẳng.",
    "gentle_left_curve": "Đường cong nhẹ sang trái.",
    "gentle_right_curve": "Đường cong nhẹ sang phải.",
    "sharp_left_curve": "Đường cua gấp sang trái.",
    "sharp_right_curve": "Đường cua gấp sang phải.",
    "sharp_curve": "Đường có khúc cua gấp.",
    "gentle_curve": "Đường có khúc cua nhẹ.",
    "unknown": "Không xác định được hình dạng đường.",
}


def describe_road_type(road_type: str) -> str:
    """Trả về mô tả tiếng Việt ngắn gọn cho một road_type - dùng khi debug hoặc build prompt."""
    return ROAD_TYPE_DESCRIPTIONS_VI.get(road_type, road_type)
