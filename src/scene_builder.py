class SceneBuilder:

    def __init__(self):
        pass

    def build(self, lane_info, ego_lane, lane_geometry, lane_width, vehicle_offset=None, lane_classification_result=None):
        """
        Xây dựng scene representation.

        Args:
            lane_info: danh sách lane info (list) - backward compatible
            ego_lane: thông tin ego lane
            lane_geometry: thông tin geometry
            lane_width: thông tin lane width
            vehicle_offset: thông tin offset
            lane_classification_result: kết quả từ classify_lanes (dict) - ưu tiên dùng
        """
        scene = {}

        # Sử dụng lane_classification_result nếu có
        if lane_classification_result is not None:
            scene["total_lane_lines"] = lane_classification_result["total_lanes"]
            scene["same_direction_lanes"] = lane_classification_result["same_direction_count"]
            scene["opposite_direction_lanes"] = len(lane_classification_result["opposite_direction_lanes"])
            scene["lane_count"] = lane_classification_result["same_direction_count"]  # Dùng cho mô tả

            # Chuyển đổi lanes với thông tin mới
            all_lanes = lane_classification_result["all_lanes"]
            lanes = []
            for lane in all_lanes:
                lane_id = lane["id"]
                lane_data = {
                    "id": lane_id,
                    "side": lane["side"],
                    "mean_x": lane["mean_x"],
                    "curvature": lane_geometry[lane_id]["curvature"] if lane_id < len(lane_geometry) else 0
                }
                if lane["side"] == "same_direction" and "same_direction_index" in lane:
                    lane_data["lane_index_in_direction"] = lane["same_direction_index"]
                lanes.append(lane_data)
            scene["lanes"] = lanes
        else:
            # Backward compatibility
            scene["lane_count"] = len(lane_info)
            scene["total_lane_lines"] = len(lane_info)

            lanes = []
            for i in range(len(lane_info)):
                lane = {
                    "id": i,
                    "side": lane_info[i]["side"],
                    "mean_x": lane_info[i]["mean_x"],
                    "curvature": lane_geometry[i]["curvature"]
                }
                lanes.append(lane)
            scene["lanes"] = lanes

        scene["ego_lane"] = {
            "index": ego_lane["ego_lane_index"],
            "same_direction_lane_index": ego_lane.get("ego_lane_same_direction_index", 1),
            "left_boundary": ego_lane["left_boundary"],
            "right_boundary": ego_lane["right_boundary"],
            "is_between_lanes": ego_lane.get("is_between_lanes", False)
        }

        if lane_width is not None:
            scene["lane_width_pixels"] = lane_width["lane_width_pixels"]

        if vehicle_offset is not None:
            scene["vehicle_offset"] = {
                "offset_pixels": vehicle_offset["offset_pixels"],
                "direction": vehicle_offset["direction"],
                "offset_ratio_percent": vehicle_offset.get("offset_ratio_percent", 0),
                "dist_from_left_boundary": vehicle_offset.get("distance_to_left_boundary", None) or vehicle_offset.get("dist_from_left_boundary", None),
                "dist_from_right_boundary": vehicle_offset.get("distance_to_right_boundary", None) or vehicle_offset.get("dist_from_right_boundary", None)
            }

        return scene