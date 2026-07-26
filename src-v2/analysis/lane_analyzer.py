"""
Phân tích làn đường: xác định ego lane, độ lệch xe, độ cong, và ngữ nghĩa từng làn.

Module này gộp 3 file cũ (đã trùng lặp một phần chức năng):
- src/lane_reasoning.py   -> xác định ego lane, offset, phân loại lane theo topology
- src/lane_curvature.py   -> ước lượng độ cong bằng vanishing point + polyfit
- src/lane_semantics.py   -> phân loại loại làn (ego/trái/phải, có đi được không)

Lý do gộp: cả 3 file đều nhận cùng input (danh sách điểm của từng làn) và
đều cần kết quả `ego_lane` để hoạt động, nên tách riêng 3 file chỉ gây khó
theo dõi thứ tự gọi. `road_topology` (ước lượng độ cong thô, dựa trên độ hội
tụ của các làn) trong lane_reasoning.py cũ đã bị XÓA khỏi module này vì
`LaneCurvatureEstimator` (dựa trên vanishing point) cho kết quả đáng tin cậy
hơn và tránh việc 2 nơi tự tính độ cong rồi ra 2 kết luận khác nhau.

BUG ĐÃ SỬA so với lane_semantics.py cũ:
    Hàm `_infer_lateral_position` cũ so sánh `lane_index < ego_left` bằng
    ORIGINAL index (thứ tự làn do model trả về) trong khi `ego_left`/`ego_right`
    cũng là original index - điều này CHỈ đúng nếu model luôn trả làn theo thứ
    tự trái->phải. Nhiều lane detector không đảm bảo điều này, nên phần tử
    "left"/"right" ngữ nghĩa có thể sai. Module này sửa lại bằng cách so sánh
    trên SORTED index (vị trí sau khi đã sắp xếp theo tọa độ x thực tế).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)

Point = Tuple[float, float]
Lane = List[Point]


# ---------------------------------------------------------------------------
# Kiểu dữ liệu ngữ nghĩa làn đường
# ---------------------------------------------------------------------------

class LaneType(str, Enum):
    """Loại làn đường. Có thể mở rộng thêm khi có model phân loại vạch kẻ thật."""
    EGO = "ego"
    NEIGHBOR = "neighbor"
    SHOULDER = "shoulder"
    UNKNOWN = "unknown"


class CurvatureClass(str, Enum):
    STRAIGHT = "straight"
    GENTLE_LEFT = "gentle_left_curve"
    GENTLE_RIGHT = "gentle_right_curve"
    SHARP_LEFT = "sharp_left_curve"
    SHARP_RIGHT = "sharp_right_curve"
    UNKNOWN = "unknown"


@dataclass
class SortedLane:
    """Một làn đường sau khi đã sắp xếp theo vị trí x (trái -> phải)."""
    original_index: int
    sorted_index: int
    points: Lane
    x_at_reference: float

    def to_dict(self) -> Dict:
        return {
            "original_index": self.original_index,
            "sorted_index": self.sorted_index,
            "x_at_reference": float(self.x_at_reference),
            "point_count": len(self.points),
        }


@dataclass
class EgoLaneInfo:
    """Kết quả xác định ego lane (làn xe đang chạy)."""
    left_boundary_index: Optional[int] = None
    right_boundary_index: Optional[int] = None
    left_boundary_sorted: Optional[int] = None
    right_boundary_sorted: Optional[int] = None
    ego_lane_center_x: float = 0.0
    lane_width: float = 0.0
    left_x: Optional[float] = None
    right_x: Optional[float] = None
    confidence: float = 0.0
    reason: str = "no_lanes"

    def to_dict(self) -> Dict:
        return {
            "left_boundary_index": self.left_boundary_index,
            "right_boundary_index": self.right_boundary_index,
            "left_boundary_sorted": self.left_boundary_sorted,
            "right_boundary_sorted": self.right_boundary_sorted,
            "ego_lane_center_x": float(self.ego_lane_center_x),
            "lane_width": float(self.lane_width),
            "confidence": float(self.confidence),
            "reason": self.reason,
        }


@dataclass
class VehicleOffset:
    """Độ lệch của xe so với tâm ego lane. Âm = lệch trái, dương = lệch phải."""
    offset_pixels: float = 0.0
    offset_ratio_percent: float = 0.0
    direction: str = "unknown"
    vehicle_x: float = 0.0
    lane_center_x: float = 0.0
    lane_width: Optional[float] = None
    distance_to_left_boundary: Optional[float] = None
    distance_to_right_boundary: Optional[float] = None
    is_vehicle_between_boundaries: bool = False

    def to_dict(self) -> Dict:
        return {
            "offset_pixels": float(self.offset_pixels),
            "offset_ratio_percent": float(self.offset_ratio_percent),
            "direction": self.direction,
            "vehicle_x": float(self.vehicle_x),
            "lane_center_x": float(self.lane_center_x),
            "lane_width": self.lane_width,
            "distance_to_left_boundary": self.distance_to_left_boundary,
            "distance_to_right_boundary": self.distance_to_right_boundary,
            "is_vehicle_between_boundaries": self.is_vehicle_between_boundaries,
        }


@dataclass
class LaneCurvature:
    """Độ cong ước lượng cho MỘT làn (dựa trên vanishing point)."""
    vanishing_point_x: Optional[float] = None
    mse_linear: float = float("inf")
    mse_quadratic: float = float("inf")
    drift_ratio: float = 0.0
    is_straight: bool = True
    confidence: float = 0.3


@dataclass
class AggregatedCurvature:
    """Độ cong tổng hợp từ nhiều làn."""
    curvature_magnitude: float = 0.0
    direction: str = "unknown"
    classification: str = "unknown"
    confidence: float = 0.0
    vanishing_point_spread: float = 0.0
    avg_drift: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "curvature_magnitude": float(self.curvature_magnitude),
            "direction": self.direction,
            "classification": self.classification,
            "confidence": float(self.confidence),
            "vanishing_point_spread": float(self.vanishing_point_spread),
            "avg_drift": float(self.avg_drift),
        }


@dataclass
class LaneSemantic:
    """Ngữ nghĩa của một làn: có phải ego lane không, đi được không, vị trí tương đối."""
    lane_index: int
    lane_type: LaneType = LaneType.UNKNOWN
    is_ego_lane: bool = False
    is_drivable: bool = True
    lateral_position: str = "unknown"  # "left" | "middle" | "right" | "edge_left" | "edge_right"

    def to_dict(self) -> Dict:
        return {
            "lane_index": self.lane_index,
            "lane_type": self.lane_type.value,
            "is_ego_lane": self.is_ego_lane,
            "is_drivable": self.is_drivable,
            "lateral_position": self.lateral_position,
        }


@dataclass
class LaneAnalysisResult:
    """Kết quả đầy đủ của bước phân tích làn đường - input cho scene_builder."""
    sorted_lanes: List[SortedLane] = field(default_factory=list)
    ego_lane: EgoLaneInfo = field(default_factory=EgoLaneInfo)
    left_neighbor_indices: List[int] = field(default_factory=list)
    right_neighbor_indices: List[int] = field(default_factory=list)
    vehicle_offset: VehicleOffset = field(default_factory=VehicleOffset)
    lane_curvatures: List[LaneCurvature] = field(default_factory=list)
    aggregated_curvature: AggregatedCurvature = field(default_factory=AggregatedCurvature)
    lane_semantics: List[LaneSemantic] = field(default_factory=list)
    image_width: int = 0
    image_height: int = 0

    def to_dict(self) -> Dict:
        return {
            "sorted_lanes": [lane.to_dict() for lane in self.sorted_lanes],
            "ego_lane": self.ego_lane.to_dict(),
            "lane_classification": {
                "left_neighbor_indices": self.left_neighbor_indices,
                "right_neighbor_indices": self.right_neighbor_indices,
                "left_neighbor_count": len(self.left_neighbor_indices),
                "right_neighbor_count": len(self.right_neighbor_indices),
            },
            "vehicle_offset": self.vehicle_offset.to_dict(),
            "curvature": self.aggregated_curvature.to_dict(),
            "lane_semantics": [s.to_dict() for s in self.lane_semantics],
            "image_width": self.image_width,
            "image_height": self.image_height,
        }


# ---------------------------------------------------------------------------
# Bộ phân tích chính
# ---------------------------------------------------------------------------

class LaneAnalyzer:
    """
    Phân tích ego-centric, dựa trên topology (KHÔNG dựa vào vị trí tuyệt đối
    trên ảnh) để xác định:
    1. Ego lane = cặp 2 vạch kề nhau bao quanh vị trí xe (giữa ảnh theo trục x)
    2. Độ lệch của xe so với tâm ego lane
    3. Độ cong của đường (dựa trên vanishing point của từng làn)
    4. Ngữ nghĩa của từng làn (ego / lân cận / có đi được không)
    """

    # Ngưỡng phân loại độ cong (đơn vị: độ lệch pixel vanishing-point / 1000, xem aggregate)
    CURVE_THRESHOLD_GENTLE = 50.0   # vanishing_point_spread (px)
    CURVE_THRESHOLD_SHARP = 200.0

    def __init__(self, vehicle_position_y_ratio: float = 0.95):
        """
        Args:
            vehicle_position_y_ratio: vị trí y của xe, tính theo tỉ lệ chiều cao ảnh
                                       (0.95 nghĩa là gần đáy ảnh - nơi camera dashcam
                                       thường "nhìn thấy" đầu xe / mép capo).
        """
        self.vehicle_position_y_ratio = vehicle_position_y_ratio

    # -- Entry point ---------------------------------------------------

    def analyze(self, lanes: List[Lane], image_width: int, image_height: int) -> LaneAnalysisResult:
        """
        Phân tích toàn bộ danh sách làn phát hiện được trên một ảnh.

        Args:
            lanes: danh sách làn, mỗi làn là danh sách điểm (x, y) theo pixel.
            image_width, image_height: kích thước ảnh gốc (dùng để suy ra vị trí xe).

        Returns:
            LaneAnalysisResult chứa toàn bộ kết quả phân tích.
        """
        if not lanes:
            logger.warning("Không có làn nào để phân tích (lanes rỗng)")
            return LaneAnalysisResult(image_width=image_width, image_height=image_height)

        sorted_lanes = self._sort_lanes_by_x(lanes, image_height)
        ego_lane = self._find_ego_lane_pair(sorted_lanes, image_width)
        left_neighbors, right_neighbors = self._classify_neighbors(sorted_lanes, ego_lane)
        vehicle_offset = self._calculate_vehicle_offset(ego_lane, image_width)

        lane_curvatures = [self.estimate_curvature(lane, image_width, image_height) for lane in lanes]
        aggregated_curvature = self.aggregate_curvature(lane_curvatures, lanes, image_width, image_height)

        lane_semantics = self._classify_lane_semantics(sorted_lanes, ego_lane)

        return LaneAnalysisResult(
            sorted_lanes=sorted_lanes,
            ego_lane=ego_lane,
            left_neighbor_indices=left_neighbors,
            right_neighbor_indices=right_neighbors,
            vehicle_offset=vehicle_offset,
            lane_curvatures=lane_curvatures,
            aggregated_curvature=aggregated_curvature,
            lane_semantics=lane_semantics,
            image_width=image_width,
            image_height=image_height,
        )

    # -- Bước 1: sắp xếp làn theo vị trí x thực tế ----------------------

    def _sort_lanes_by_x(self, lanes: List[Lane], image_height: int) -> List[SortedLane]:
        """Sắp xếp làn trái -> phải dựa trên tọa độ x tại vị trí gần đáy ảnh (nơi xe đứng)."""
        reference_y = int(image_height * self.vehicle_position_y_ratio)

        entries = []
        for i, lane in enumerate(lanes):
            x_at_ref = self._get_x_at_y(lane, reference_y)
            entries.append((i, lane, x_at_ref if x_at_ref is not None else float("inf")))

        entries.sort(key=lambda e: e[2])

        return [
            SortedLane(original_index=orig_idx, sorted_index=sorted_idx, points=lane, x_at_reference=x_ref)
            for sorted_idx, (orig_idx, lane, x_ref) in enumerate(entries)
        ]

    def _get_x_at_y(self, lane_points: Lane, y_target: int, search_range: int = 30) -> Optional[float]:
        """Nội suy tọa độ x tại một y cho trước, dùng các điểm gần y_target nhất."""
        if not lane_points:
            return None

        nearby = [p for p in lane_points if abs(p[1] - y_target) <= search_range]
        if nearby:
            return float(np.mean([p[0] for p in nearby]))

        closest = min(lane_points, key=lambda p: abs(p[1] - y_target))
        if abs(closest[1] - y_target) > search_range * 2:
            return None
        return float(closest[0])

    # -- Bước 2: xác định ego lane (cặp vạch kề nhau bao quanh xe) ------

    def _find_ego_lane_pair(self, sorted_lanes: List[SortedLane], image_width: int) -> EgoLaneInfo:
        """
        Tìm cặp làn kề nhau tạo thành ego lane.

        Ý tưởng cốt lõi: camera dashcam thường được gắn giữa xe, nên ego lane
        là cặp vạch kề nhau có TÂM gần với tâm ảnh (image_width / 2) nhất.
        Với n làn phát hiện được, có (n-1) cặp kề nhau khả dĩ - ta chấm điểm
        từng cặp và chọn cặp tốt nhất thay vì giả định vị trí cố định.
        """
        n = len(sorted_lanes)
        vehicle_x = image_width / 2

        if n == 1:
            return EgoLaneInfo(
                right_boundary_index=sorted_lanes[0].original_index,
                right_boundary_sorted=0,
                ego_lane_center_x=sorted_lanes[0].x_at_reference,
                confidence=0.5,
                reason="only_one_lane_visible",
            )

        best_sorted_idx = 0
        best_score = float("inf")
        expected_width = image_width * 0.15  # bề rộng làn "điển hình" ~ 15% chiều rộng ảnh

        for i in range(n - 1):
            left, right = sorted_lanes[i], sorted_lanes[i + 1]
            lane_center_x = (left.x_at_reference + right.x_at_reference) / 2
            score = abs(lane_center_x - vehicle_x)

            # Ưu tiên mạnh cặp làn mà xe thực sự nằm giữa 2 vạch
            if left.x_at_reference < vehicle_x < right.x_at_reference:
                score *= 0.5

            # Phạt nhẹ nếu bề rộng làn quá lệch so với bề rộng điển hình
            lane_width = right.x_at_reference - left.x_at_reference
            if lane_width > 0:
                width_penalty = abs(lane_width - expected_width) / expected_width
                score *= (1 + width_penalty * 0.2)

            if score < best_score:
                best_score = score
                best_sorted_idx = i

        left, right = sorted_lanes[best_sorted_idx], sorted_lanes[best_sorted_idx + 1]
        lane_center_x = (left.x_at_reference + right.x_at_reference) / 2
        lane_width = right.x_at_reference - left.x_at_reference
        dist_to_center = abs(lane_center_x - vehicle_x)

        if dist_to_center < image_width * 0.1:
            confidence = 0.95
        elif dist_to_center < image_width * 0.25:
            confidence = 0.8
        elif dist_to_center < image_width * 0.4:
            confidence = 0.6
        else:
            confidence = 0.4

        return EgoLaneInfo(
            left_boundary_index=left.original_index,
            right_boundary_index=right.original_index,
            left_boundary_sorted=left.sorted_index,
            right_boundary_sorted=right.sorted_index,
            ego_lane_center_x=lane_center_x,
            lane_width=lane_width,
            left_x=left.x_at_reference,
            right_x=right.x_at_reference,
            confidence=confidence,
            reason="best_adjacent_pair",
        )

    # -- Bước 3: phân loại làn lân cận -----------------------------------

    def _classify_neighbors(
        self, sorted_lanes: List[SortedLane], ego_lane: EgoLaneInfo
    ) -> Tuple[List[int], List[int]]:
        """Chia các làn còn lại thành nhóm bên trái / bên phải ego lane (theo sorted_index)."""
        left_bound = ego_lane.left_boundary_sorted
        right_bound = ego_lane.right_boundary_sorted

        if left_bound is None or right_bound is None:
            return [], []

        left_neighbors = [lane.original_index for lane in sorted_lanes if lane.sorted_index < left_bound]
        right_neighbors = [lane.original_index for lane in sorted_lanes if lane.sorted_index > right_bound]
        return left_neighbors, right_neighbors

    # -- Bước 4: độ lệch của xe so với tâm ego lane ----------------------

    def _calculate_vehicle_offset(self, ego_lane: EgoLaneInfo, image_width: int) -> VehicleOffset:
        """
        Tính độ lệch của xe so với tâm ego lane.

        Giả định: camera được gắn ở tâm xe, nên vị trí xe trên ảnh luôn là
        image_width / 2. offset > 0 nghĩa là tâm làn nằm bên trái tâm xe,
        tức xe đang lệch VỀ BÊN PHẢI so với tâm làn.
        """
        vehicle_x = image_width / 2
        lane_center_x = ego_lane.ego_lane_center_x
        offset_pixels = vehicle_x - lane_center_x

        lane_width = ego_lane.lane_width
        offset_ratio = (offset_pixels / lane_width) * 100 if lane_width > 0 else 0.0

        if abs(offset_pixels) < 10:
            direction = "centered"
        elif offset_pixels > 0:
            direction = "right_of_lane_center"
        else:
            direction = "left_of_lane_center"

        left_x = ego_lane.left_x
        right_x = ego_lane.right_x
        dist_to_left = (vehicle_x - left_x) if left_x is not None else None
        dist_to_right = (right_x - vehicle_x) if right_x is not None else None
        is_between = (left_x is not None and right_x is not None and left_x < vehicle_x < right_x)

        return VehicleOffset(
            offset_pixels=offset_pixels,
            offset_ratio_percent=offset_ratio,
            direction=direction,
            vehicle_x=vehicle_x,
            lane_center_x=lane_center_x,
            lane_width=lane_width if lane_width > 0 else None,
            distance_to_left_boundary=dist_to_left,
            distance_to_right_boundary=dist_to_right,
            is_vehicle_between_boundaries=is_between,
        )

    # -- Độ cong: vanishing point + polyfit ------------------------------

    def estimate_curvature(self, lane_points: Lane, image_width: int, image_height: int) -> LaneCurvature:
        """
        Ước lượng độ cong của MỘT làn dựa trên phân tích vanishing point.

        Ý tưởng: với các làn song song trên đường thẳng, điểm hội tụ phối cảnh
        (vanishing point) của chúng phải trùng nhau. Ta fit đa thức bậc 1
        (đường thẳng) và bậc 2 (parabol) qua các điểm của làn theo trục y
        (độ sâu, đã chuẩn hóa [0,1]); nếu fit bậc 1 đã khớp tốt (MSE thấp),
        làn gần như thẳng theo phối cảnh. `drift_ratio` đo mức lệch khỏi một
        đường thẳng lý tưởng, chuẩn hóa theo chiều rộng ảnh để so sánh được
        giữa các ảnh có độ phân giải khác nhau.
        """
        if len(lane_points) < 4:
            return LaneCurvature()

        points = np.array(lane_points, dtype=np.float64)
        valid = (points[:, 0] > 0) & (points[:, 0] < image_width) & \
                (points[:, 1] > 0) & (points[:, 1] < image_height)
        points = points[valid]
        if len(points) < 4:
            return LaneCurvature()

        points = points[np.argsort(points[:, 1])]
        y_vals, x_vals = points[:, 1], points[:, 0]
        y_min, y_max = float(np.min(y_vals)), float(np.max(y_vals))
        y_norm = (y_vals - y_min) / max(y_max - y_min, 1)

        try:
            coeffs_linear = np.polyfit(y_norm, x_vals, deg=1)
            mse_linear = float(np.mean((x_vals - np.polyval(coeffs_linear, y_norm)) ** 2))
        except (np.linalg.LinAlgError, ValueError):
            mse_linear = float("inf")

        try:
            coeffs_quad = np.polyfit(y_norm, x_vals, deg=2)
            mse_quad = float(np.mean((x_vals - np.polyval(coeffs_quad, y_norm)) ** 2))
            vp_x = float(coeffs_quad[2])  # x tại y_norm=0 (đỉnh ảnh) xấp xỉ vanishing point
        except (np.linalg.LinAlgError, ValueError):
            mse_quad = float("inf")
            vp_x = float(x_vals[0])

        drift_ratio = np.sqrt(mse_linear) / max(image_width, 1) if np.isfinite(mse_linear) else 1.0

        return LaneCurvature(
            vanishing_point_x=vp_x,
            mse_linear=mse_linear,
            mse_quadratic=mse_quad,
            drift_ratio=float(drift_ratio),
            is_straight=mse_linear < 1000,
            confidence=0.7 if mse_linear < 1000 else 0.5,
        )

    def aggregate_curvature(
        self,
        lane_curvatures: List[LaneCurvature],
        lanes: Optional[List[Lane]],
        image_width: int,
        image_height: int,
    ) -> AggregatedCurvature:
        """
        Gộp độ cong của nhiều làn thành một kết luận chung cho cả đường.

        Đường thẳng thật sự thì vanishing point của các làn phải GẦN NHAU
        (spread thấp) và drift trung bình thấp. Nếu spread lớn, các làn
        đang "chỉ" về các hướng khác nhau -> đường cong.
        """
        if not lane_curvatures:
            return AggregatedCurvature()

        vps = [c.vanishing_point_x for c in lane_curvatures if c.vanishing_point_x is not None]
        drift_ratios = [c.drift_ratio for c in lane_curvatures]
        straight_count = sum(1 for c in lane_curvatures if c.is_straight)

        vp_spread = (max(vps) - min(vps)) if len(vps) >= 2 else 0.0
        avg_drift = float(np.mean(drift_ratios)) if drift_ratios else 0.0
        straight_ratio = straight_count / len(lane_curvatures)

        direction = self._estimate_direction(lanes, image_width, image_height) if lanes else "straight"

        if vp_spread < 50 and avg_drift < 0.1 and straight_ratio > 0.5:
            classification = "straight"
            confidence = min(0.9, 0.6 + straight_ratio * 0.3)
            magnitude = vp_spread / 1000
        elif vp_spread > 200 or avg_drift > 0.3:
            classification = f"sharp_{direction}_curve" if direction != "straight" else "sharp_curve"
            confidence = 0.7
            magnitude = (vp_spread + avg_drift * 1000) / 100
        else:
            classification = f"gentle_{direction}_curve" if direction != "straight" else "gentle_curve"
            confidence = 0.6
            magnitude = (vp_spread + avg_drift * 500) / 500

        return AggregatedCurvature(
            curvature_magnitude=float(magnitude),
            direction=direction,
            classification=classification,
            confidence=float(confidence),
            vanishing_point_spread=float(vp_spread),
            avg_drift=float(avg_drift),
        )

    def _estimate_direction(self, lanes: List[Lane], image_width: int, image_height: int) -> str:
        """Suy ra hướng cong (trái/phải) từ độ dịch chuyển x trung bình giữa đáy và đỉnh ảnh."""
        if not lanes or len(lanes) < 2:
            return "straight"

        y_bottom, y_top = int(image_height * 0.85), int(image_height * 0.35)
        shifts = []
        for lane in lanes:
            arr = np.array(lane, dtype=np.float64)
            if arr.size == 0:
                continue
            valid = (arr[:, 0] > 0) & (arr[:, 1] > 0)
            arr = arr[valid]
            if len(arr) < 3:
                continue
            bottom_pts = arr[np.abs(arr[:, 1] - y_bottom) < 80]
            top_pts = arr[np.abs(arr[:, 1] - y_top) < 80]
            if len(bottom_pts) > 0 and len(top_pts) > 0:
                shifts.append(float(np.mean(bottom_pts[:, 0]) - np.mean(top_pts[:, 0])))

        if not shifts:
            return "straight"

        shift_ratio = float(np.mean(shifts)) / image_width
        if abs(shift_ratio) < 0.08:
            return "straight"
        return "right" if shift_ratio > 0 else "left"

    # -- Ngữ nghĩa từng làn ------------------------------------------------

    def _classify_lane_semantics(
        self, sorted_lanes: List[SortedLane], ego_lane: EgoLaneInfo
    ) -> List[LaneSemantic]:
        """
        Gán ngữ nghĩa (ego / lân cận / mép đường) cho từng làn.

        Dùng sorted_index (không dùng original_index) để tránh bug đã mô tả
        ở đầu file: original_index chỉ là thứ tự model trả về, không đảm bảo
        đúng thứ tự trái-phải trên ảnh.
        """
        n = len(sorted_lanes)
        left_bound = ego_lane.left_boundary_sorted
        right_bound = ego_lane.right_boundary_sorted

        semantics = []
        for lane in sorted_lanes:
            is_ego = lane.sorted_index in (left_bound, right_bound)

            if left_bound is not None and right_bound is not None and lane.sorted_index in (left_bound, right_bound):
                lateral_position = "middle"
                lane_type = LaneType.EGO
            elif left_bound is not None and lane.sorted_index < left_bound:
                lateral_position = "edge_left" if lane.sorted_index == 0 else "left"
                lane_type = LaneType.SHOULDER if lane.sorted_index == 0 else LaneType.NEIGHBOR
            elif right_bound is not None and lane.sorted_index > right_bound:
                lateral_position = "edge_right" if lane.sorted_index == n - 1 else "right"
                lane_type = LaneType.SHOULDER if lane.sorted_index == n - 1 else LaneType.NEIGHBOR
            else:
                lateral_position = "unknown"
                lane_type = LaneType.UNKNOWN

            semantics.append(
                LaneSemantic(
                    lane_index=lane.original_index,
                    lane_type=lane_type,
                    is_ego_lane=is_ego,
                    is_drivable=lane_type != LaneType.SHOULDER,
                    lateral_position=lateral_position,
                )
            )
        return semantics


def analyze_lanes(lanes: List[Lane], image_width: int, image_height: int) -> LaneAnalysisResult:
    """Hàm tiện ích: tạo LaneAnalyzer mặc định và phân tích ngay."""
    return LaneAnalyzer().analyze(lanes, image_width, image_height)
