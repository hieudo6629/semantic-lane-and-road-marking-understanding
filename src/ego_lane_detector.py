import numpy as np


class EgoLaneDetector:

    def __init__(self, offset_threshold=0.3):
        """
        Args:
            offset_threshold: ngưỡng offset để xác định xe có đang lệch khỏi lane center không (0-1)
        """
        self.offset_threshold = offset_threshold

    def detect(self, lane_info, image_width):
        """
        Detect ego lane - làn xe đang chạy.

        CHỈ detect trong các làn CÙNG CHIỀU (same_direction).
        Nếu lane_info có thông tin side, ưu tiên lanes cùng chiều.

        Args:
            lane_info: danh sách các lane đã classify (sorted từ trái sang phải)
            image_width: chiều rộng ảnh

        Returns:
            dict chứa ego_lane_index, left_boundary, right_boundary, và is_between_lanes
        """
        # CHỈ lấy các lanes CÙNG CHIỀU
        same_direction_lanes = []
        for i, lane in enumerate(lane_info):
            # Kiểm tra có side info không
            if lane.get("side") == "same_direction":
                same_direction_lanes.append({
                    "original_index": i,  # Index trong lane_info gốc
                    "index_in_same_dir": len(same_direction_lanes),
                    "mean_x": lane["mean_x"],
                    "same_direction_index": lane.get("same_direction_index")
                })

        # Nếu không có lane cùng chiều nào, fallback về tất cả
        if not same_direction_lanes:
            same_direction_lanes = [
                {"original_index": i, "index_in_same_dir": i, "mean_x": lane["mean_x"]}
                for i, lane in enumerate(lane_info)
            ]

        center_x = image_width / 2

        # Sắp xếp theo khoảng cách đến center
        for lane in same_direction_lanes:
            lane["dist_to_center"] = abs(lane["mean_x"] - center_x)

        same_direction_lanes.sort(key=lambda x: x["dist_to_center"])

        # Lấy 2 lane gần center nhất
        closest_1 = same_direction_lanes[0]
        closest_2 = same_direction_lanes[1] if len(same_direction_lanes) > 1 else None

        # Kiểm tra xem xe có đang ở giữa 2 lane không
        is_between_lanes = False
        ego_lane_original_idx = closest_1["original_index"]

        if closest_2:
            dist1 = closest_1["dist_to_center"]
            dist2 = closest_2["dist_to_center"]

            # Nếu 2 lane cách center tương đương (chênh nhau < 30%)
            if dist1 > 0 and abs(dist1 - dist2) / dist1 < 0.3:
                is_between_lanes = True

        # Xác định left và right boundary (trong cùng chiều)
        same_dir_count = len(same_direction_lanes)
        same_dir_ego_idx = closest_1["index_in_same_dir"]

        left_boundary = None
        right_boundary = None

        if same_dir_ego_idx > 0:
            left_boundary = same_direction_lanes[same_dir_ego_idx - 1]["original_index"]
        if same_dir_ego_idx < same_dir_count - 1:
            right_boundary = same_direction_lanes[same_dir_ego_idx + 1]["original_index"]

        result = {
            # Index trong lane_info gốc (để tương thích)
            "ego_lane_index": ego_lane_original_idx,
            # Index trong cùng chiều (1-based cho human readable)
            "ego_lane_same_direction_index": closest_1["index_in_same_dir"] + 1,
            "left_boundary": left_boundary,
            "right_boundary": right_boundary,
            "is_between_lanes": is_between_lanes,
            "distance_to_center": float(closest_1["dist_to_center"]),
            "same_direction_lane_count": same_dir_count
        }

        return result

    def detect_with_context(self, lane_info, image_width, lane_geometry=None):
        """
        Detect ego lane với context bổ sung.

        Args:
            lane_info: danh sách các lane đã classify
            image_width: chiều rộng ảnh
            lane_geometry: thông tin geometry của lanes (để xác định xu hướng)

        Returns:
            dict với thông tin chi tiết hơn
        """
        result = self.detect(lane_info, image_width)
        return result