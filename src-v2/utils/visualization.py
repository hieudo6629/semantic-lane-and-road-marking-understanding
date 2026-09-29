"""
Vẽ overlay trực quan: làn đường, hành lang (corridor) của ego lane, vị trí
xe, và biển báo phát hiện được - lên ảnh gốc.

Refactor + gộp từ:
- src/corridor_visualizer.py -> vẽ lane/corridor/vehicle (đã dùng thật trong main.py)
- Đoạn code vẽ bbox biển báo từng nằm INLINE trực tiếp trong main.py (--signs),
  không tái sử dụng được - nay gộp vào cùng 1 hàm visualize_scene() để vẽ được
  cả lane lẫn sign trên cùng một ảnh.

2 BUG ĐÃ SỬA (âm thầm sai, không crash - rất khó nhận ra khi chỉ nhìn ảnh xuất ra):

1. `_draw_lanes()` cũ kiểm tra:
       if 'ego_lane' in sorted_lanes[i] if isinstance(sorted_lanes[i], dict) else False:
   Nhưng mỗi phần tử của `sorted_lanes` (dict trả về bởi LaneReasoner) KHÔNG
   BAO GIỜ có key tên 'ego_lane' - điều kiện này luôn False. Hậu quả: ego lane
   không bao giờ được tô màu xanh nổi bật như thiết kế, mọi làn đều vẽ cùng
   màu xám mặc định. Thêm nữa, `sorted_lanes[i]` dùng `i` là index theo thứ
   tự GỐC (từ enumerate(lanes)), trong khi `sorted_lanes` lại là danh sách đã
   SẮP XẾP theo x - tức là dù sửa được lỗi key, vẫn tra nhầm phần tử.

2. `_draw_annotations()` cũ đọc:
       lane_classification = ego_lane_info.get('lane_classification', {})
   Nhưng `ego_lane_info` chính là dict của RIÊNG ego lane (left_boundary_index,
   right_boundary_index, ...) - không hề chứa key 'lane_classification' (key
   đó nằm ở cấp ngoài cùng của kết quả LaneReasoner, là một dict ANH EM chứ
   không phải con của ego_lane). Kết quả: số làn lân cận trái/phải trên ảnh
   LUÔN hiển thị "0" bất kể thực tế bao nhiêu làn.

Cách sửa triệt để: dùng thẳng các dataclass có kiểu rõ ràng từ
analysis/lane_analyzer.py (LaneAnalysisResult, EgoLaneInfo, ...) thay vì dict
lồng nhau không có kiểu - lỗi tra nhầm key như trên không thể xảy ra được nữa
vì trình soạn thảo/type-checker sẽ báo ngay nếu truy cập sai thuộc tính.
"""

from typing import List, Optional

import cv2
import numpy as np

from analysis.lane_analyzer import Lane, LaneAnalysisResult
from analysis.scene_summarizer import _summarize_offset
from perception.sign_detector import DetectedSign
from utils.logger import get_logger

logger = get_logger(__name__)

# Màu BGR (định dạng OpenCV, không phải RGB)
COLORS = {
    "ego_lane": (0, 255, 0),
    "ego_lane_fill": (0, 100, 0),
    "other_lane": (180, 180, 180),
    "lane_center": (0, 255, 255),
    "vehicle": (0, 0, 255),
    "text": (255, 255, 255),
    "sign_box": (0, 255, 255),
    "sign_box_critical": (0, 0, 255),
    "background": (40, 40, 40),
}


class SceneVisualizer:
    """Vẽ overlay đầy đủ (làn đường + corridor + xe + biển báo) lên một ảnh."""

    def __init__(self, image_width: int = 1640, image_height: int = 590):
        self.image_width = image_width
        self.image_height = image_height

    def visualize(
        self,
        image: Optional[np.ndarray],
        lanes: List[Lane],
        lane_result: LaneAnalysisResult,
        detected_signs: Optional[List[DetectedSign]] = None,
        show_annotations: bool = True,
    ) -> np.ndarray:
        """
        Args:
            image: ảnh gốc (sẽ được copy, không chỉnh sửa ảnh gốc) hoặc None để vẽ trên nền trống.
            lanes: danh sách làn gốc (điểm (x, y)), THEO ĐÚNG THỨ TỰ đã đưa vào LaneAnalyzer.analyze().
            lane_result: kết quả LaneAnalyzer.analyze() tương ứng với `lanes`.
            detected_signs: biển báo phát hiện được trên cùng ảnh (tùy chọn).
            show_annotations: có vẽ chữ chú thích (offset, số làn lân cận...) hay không.
        """
        if image is None:
            vis = np.full((self.image_height, self.image_width, 3), 40, dtype=np.uint8)
        else:
            vis = image.copy()
            if vis.ndim == 2:
                vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

        ego = lane_result.ego_lane
        ego_original_indices = {ego.left_boundary_index, ego.right_boundary_index} - {None}

        self._draw_lanes(vis, lanes, ego_original_indices)
        self._fill_ego_corridor(vis, lanes, ego)
        self._draw_lane_center(vis, lanes, ego)
        self._draw_vehicle(vis, lane_result.vehicle_offset)

        if detected_signs:
            self._draw_signs(vis, detected_signs)

        if show_annotations:
            self._draw_annotations(vis, lane_result, lane_count=len(lanes) - 1 if lanes else 0)

        return vis

    def _draw_lanes(self, vis: np.ndarray, lanes: List[Lane], ego_original_indices: set) -> None:
        """Vẽ tất cả các đường làn; làn thuộc ego lane được tô xanh đậm hơn, còn lại tô xám."""
        for original_index, lane_points in enumerate(lanes):
            if not lane_points or len(lane_points) < 2:
                continue

            pts = np.array(lane_points, dtype=np.int32)
            is_ego_boundary = original_index in ego_original_indices
            color = COLORS["ego_lane"] if is_ego_boundary else COLORS["other_lane"]
            thickness = 3 if is_ego_boundary else 2

            cv2.polylines(vis, [pts], isClosed=False, color=color, thickness=thickness, lineType=cv2.LINE_AA)

    def _fill_ego_corridor(self, vis: np.ndarray, lanes: List[Lane], ego) -> None:
        """Tô màu bán trong suốt vùng hành lang (corridor) giữa 2 vạch biên ego lane."""
        left_idx, right_idx = ego.left_boundary_index, ego.right_boundary_index
        if left_idx is None or right_idx is None:
            return
        if left_idx >= len(lanes) or right_idx >= len(lanes):
            return

        left_lane = sorted(lanes[left_idx], key=lambda p: -p[1])  # trên -> dưới
        right_lane = sorted(lanes[right_idx], key=lambda p: -p[1])
        if not left_lane or not right_lane:
            return

        fill_pts = [[p[0], p[1]] for p in left_lane] + [[p[0], p[1]] for p in reversed(right_lane)]
        if len(fill_pts) <= 2:
            return

        overlay = vis.copy()
        cv2.fillPoly(overlay, [np.array(fill_pts, dtype=np.int32)], COLORS["ego_lane_fill"])
        cv2.addWeighted(vis, 0.7, overlay, 0.3, 0, vis)

    def _draw_lane_center(self, vis: np.ndarray, lanes: List[Lane], ego) -> None:
        """Vẽ đường thẳng đứng đánh dấu tâm ego lane, gần đáy ảnh."""
        left_idx, right_idx = ego.left_boundary_index, ego.right_boundary_index
        if left_idx is None or right_idx is None or left_idx >= len(lanes) or right_idx >= len(lanes):
            return

        sample_y = int(self.image_height * 0.8)
        left_x = self._get_x_at_y(lanes[left_idx], sample_y)
        right_x = self._get_x_at_y(lanes[right_idx], sample_y)
        if left_x is None or right_x is None:
            return

        center_x = int((left_x + right_x) / 2)
        cv2.line(vis, (center_x, sample_y), (center_x, int(sample_y * 0.5)), COLORS["lane_center"], 2, cv2.LINE_AA)

    def _draw_vehicle(self, vis: np.ndarray, offset) -> None:
        """Vẽ hình chữ nhật + mũi tên đại diện vị trí xe (giả định gắn camera ở tâm xe)."""
        vehicle_x = offset.vehicle_x if offset.vehicle_x else self.image_width / 2
        vehicle_y = int(self.image_height * 0.95)

        w, h = 60, 30
        top_left = (int(vehicle_x - w / 2), int(vehicle_y - h / 2))
        bottom_right = (int(vehicle_x + w / 2), int(vehicle_y + h / 2))
        cv2.rectangle(vis, top_left, bottom_right, COLORS["vehicle"], -1)
        cv2.rectangle(vis, top_left, bottom_right, (255, 255, 255), 2)
        cv2.arrowedLine(vis, (int(vehicle_x), vehicle_y), (int(vehicle_x), vehicle_y - 40), (255, 255, 255), 2, tipLength=0.3)

    def _draw_signs(self, vis: np.ndarray, detected_signs: List[DetectedSign]) -> None:
        """Vẽ khung bao + nhãn cho từng biển báo phát hiện được."""
        critical_types = {"stop", "no_entry", "traffic_light_red"}
        for sign in detected_signs:
            x1, y1, x2, y2 = sign.bbox
            color = COLORS["sign_box_critical"] if sign.sign_type in critical_types else COLORS["sign_box"]
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            label = f"{sign.sign_type} {sign.confidence:.0%}"
            cv2.putText(vis, label, (x1, max(y1 - 10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def _draw_annotations(self, vis: np.ndarray, lane_result: LaneAnalysisResult, lane_count: int = 0) -> None:
        """Vẽ chữ chú thích: ego lane, offset, số làn lân cận - lấy trực tiếp từ dataclass, không tra dict sai key."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        y = 30
        ego = lane_result.ego_lane
        offset_summary = _summarize_offset(lane_result.vehicle_offset.to_dict())
        left_count = len(lane_result.left_neighbor_indices)
        # Vị trí làn ego dạng "k/n" (k = left_count+1), giống hệt cách tính
        # trong scene_summarizer.py - KHÔNG dùng left_boundary_index/right_boundary_index
        # (chỉ số nội bộ gốc của UFLD-v2 trước khi sắp xếp, không phải thứ tự làn).
        ego_position = f"{left_count + 1}/{lane_count}" if lane_count > 0 else "unknown"

        lines = [
            f"Ego Lane: {ego_position} (conf {ego.confidence:.2f})",
            f"Offset: {offset_summary['direction']}, {offset_summary['magnitude']} ({offset_summary['offset_percent']}%)",
            f"Left neighbors: {len(lane_result.left_neighbor_indices)}, "
            f"Right neighbors: {len(lane_result.right_neighbor_indices)}",
            f"Road curvature: {lane_result.aggregated_curvature.classification}",
        ]
        for text in lines:
            cv2.putText(vis, text, (20, y), font, 0.6, COLORS["text"], 1, cv2.LINE_AA)
            y += 25

    def _get_x_at_y(self, lane_points: Lane, y_target: int, search_range: int = 30) -> Optional[float]:
        nearby = [p[0] for p in lane_points if abs(p[1] - y_target) <= search_range]
        if nearby:
            return float(np.mean(nearby))
        closest = min(lane_points, key=lambda p: abs(p[1] - y_target))
        if abs(closest[1] - y_target) <= search_range * 2:
            return float(closest[0])
        return None


def visualize_scene(
    image: Optional[np.ndarray],
    lanes: List[Lane],
    lane_result: LaneAnalysisResult,
    detected_signs: Optional[List[DetectedSign]] = None,
) -> np.ndarray:
    """Hàm tiện ích: tạo SceneVisualizer với kích thước lấy từ ảnh (hoặc từ lane_result) rồi vẽ ngay."""
    width = image.shape[1] if image is not None else lane_result.image_width
    height = image.shape[0] if image is not None else lane_result.image_height
    return SceneVisualizer(width, height).visualize(image, lanes, lane_result, detected_signs=detected_signs)
