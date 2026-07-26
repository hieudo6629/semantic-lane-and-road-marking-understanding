import numpy as np


class VehicleOffsetEstimator:

    def __init__(self):
        pass

    def estimate(self, lanes, ego_lane_index, image_width, image_height, lane_geometry=None):
        """
        Ước lượng độ lệch của xe so với center của ego lane.

        Args:
            lanes: danh sách các lane points
            ego_lane_index: chỉ số của ego lane
            image_width: chiều rộng ảnh
            image_height: chiều cao ảnh
            lane_geometry: thông tin geometry của lanes (tùy chọn)

        Returns:
            dict chứa thông tin offset
        """
        if ego_lane_index is None:
            return None

        ego_lane = lanes[ego_lane_index]

        # Lấy tọa độ y gần bottom của image (xe đang ở đó)
        y_offset = image_height - 50  # 50 pixels từ bottom
        y_eval = min(y_offset, image_height - 1)

        # Nếu có lane_geometry (polynomial coefficients), sử dụng để tính center
        if lane_geometry is not None and ego_lane_index < len(lane_geometry):
            coeffs = lane_geometry[ego_lane_index]["coefficients"]
            lane_center_x = coeffs["a"] * (y_eval ** 2) + coeffs["b"] * y_eval + coeffs["c"]
        else:
            # Fallback: lấy mean x của các điểm gần bottom
            bottom_points = [p for p in ego_lane if p[1] >= y_offset - 30]
            if bottom_points:
                lane_center_x = np.mean([p[0] for p in bottom_points])
            else:
                # Lấy điểm có y lớn nhất
                bottom_point = max(ego_lane, key=lambda p: p[1])
                lane_center_x = bottom_point[0]

        # Vị trí xe (假设 xe ở center ngang của image)
        vehicle_x = image_width / 2

        # Tính offset
        offset_pixels = vehicle_x - lane_center_x
        offset_normalized = offset_pixels / (image_width / 2)  # normalize về [-1, 1]

        # Xác định hướng lệch
        if abs(offset_pixels) < 5:  # ngưỡng 5 pixels
            direction = "centered"
        elif offset_pixels > 0:
            direction = "right_of_center"
        else:
            direction = "left_of_center"

        # Ước lượng độ lệch theo tỷ lệ (%)
        lane_width = self._estimate_lane_width(lanes, ego_lane_index, y_offset)
        offset_ratio = (offset_pixels / lane_width * 100) if lane_width > 0 else 0

        return {
            "offset_pixels": float(offset_pixels),
            "offset_normalized": float(offset_normalized),
            "offset_ratio_percent": float(offset_ratio),
            "direction": direction,
            "vehicle_x": float(vehicle_x),
            "lane_center_x": float(lane_center_x),
            "y_evaluation_point": float(y_eval),
            "lane_width_for_reference": float(lane_width)
        }

    def _estimate_lane_width(self, lanes, ego_lane_index, y_target):
        """
        Ước lượng chiều rộng lane tại một điểm y cụ thể.
        """
        ego_lane = lanes[ego_lane_index]

        # Lấy tọa độ x tại y gần y_target
        nearby_points = [p for p in ego_lane if abs(p[1] - y_target) < 30]

        if nearby_points:
            left_x = min(p[0] for p in nearby_points)
            right_x = max(p[0] for p in nearby_points)
            return right_x - left_x

        return 0

    def estimate_with_boundaries(self, lanes, ego_lane_info, image_width, image_height, lane_geometry=None):
        """
        Ước lượng offset với thông tin left/right boundaries của ego lane.

        Args:
            lanes: danh sách các lane points
            ego_lane_info: dict chứa ego_lane_index, left_boundary, right_boundary
            image_width: chiều rộng ảnh
            image_height: chiều cao ảnh
            lane_geometry: thông tin geometry của lanes (tùy chọn)

        Returns:
            dict chứa thông tin offset chi tiết hơn
        """
        ego_idx = ego_lane_info["ego_lane_index"]
        left_idx = ego_lane_info["left_boundary"]
        right_idx = ego_lane_info["right_boundary"]

        y_eval = image_height - 50

        if left_idx is None or right_idx is None:
            return self.estimate(lanes, ego_idx, image_width, image_height, lane_geometry)

        left_lane = lanes[left_idx]
        right_lane = lanes[right_idx]

        # Lấy điểm left boundary gần bottom
        left_points = [p for p in left_lane if abs(p[1] - y_eval) < 30]
        left_x = np.mean([p[0] for p in left_points]) if left_points else left_lane[-1][0]

        # Lấy điểm right boundary gần bottom
        right_points = [p for p in right_lane if abs(p[1] - y_eval) < 30]
        right_x = np.mean([p[0] for p in right_points]) if right_points else right_lane[-1][0]

        # Center của lane
        lane_center_x = (left_x + right_x) / 2

        # Vị trí xe
        vehicle_x = image_width / 2

        # Offset
        offset_pixels = vehicle_x - lane_center_x
        lane_width = right_x - left_x

        # Direction
        if abs(offset_pixels) < 5:
            direction = "centered"
        elif offset_pixels > 0:
            direction = "right_of_center"
        else:
            direction = "left_of_center"

        # Khoảng cách đến 2 boundary
        dist_to_left = vehicle_x - left_x
        dist_to_right = right_x - vehicle_x

        return {
            "offset_pixels": float(offset_pixels),
            "direction": direction,
            "vehicle_x": float(vehicle_x),
            "lane_center_x": float(lane_center_x),
            "lane_width": float(lane_width),
            "distance_to_left_boundary": float(dist_to_left),
            "distance_to_right_boundary": float(dist_to_right),
            "offset_ratio_percent": float((offset_pixels / lane_width * 100) if lane_width > 0 else 0)
        }