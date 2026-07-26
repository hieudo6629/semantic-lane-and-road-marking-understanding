class SceneDescription:

    def __init__(self):
        pass

    def generate(self, scene, road_info):
        """
        Tạo mô tả cảnh giao thông.

        Phân biệt:
        - same_direction_lanes: số làn cùng chiều (đang đi)
        - total_lane_lines: tổng số lane lines (cả 2 chiều)
        """
        same_dir_lanes = scene.get("same_direction_lanes", scene.get("lane_count", 0))
        total_lines = scene.get("total_lane_lines", 0)

        # Ưu tiên dùng ego_lane_same_direction_index nếu có, fallback về ego_lane_index
        ego_info = scene.get("ego_lane", {})
        ego_idx = ego_info.get("same_direction_lane_index", ego_info.get("index", 0))
        # Nếu same_direction_lane_index bị None, cộng thêm 1 để đổi 0-based -> 1-based
        if ego_idx == 0 and "same_direction_lane_index" in ego_info:
            ego_idx = ego_info["same_direction_lane_index"]

        road_type = road_info["road_type"]

        text = f"The vehicle is traveling in lane {ego_idx} of a {same_dir_lanes}-lane road. "

        if road_type == "straight":
            text += "The road ahead is straight."
        elif road_type == "left_curve":
            text += "The road ahead curves to the left."
        else:
            text += "The road ahead curves to the right."

        # Thêm thông tin về làn ngược chiều
        opposite_lanes = scene.get("opposite_direction_lanes", 0)
        if opposite_lanes > 0 and total_lines > same_dir_lanes:
            text += f" There are {opposite_lanes} lane(s) for oncoming traffic on the opposite side."

        # Thêm thông tin vehicle offset
        if "vehicle_offset" in scene:
            offset = scene["vehicle_offset"]
            direction = offset["direction"]
            offset_ratio = abs(offset["offset_ratio_percent"])

            if direction == "centered":
                text += " The vehicle is well-centered within its lane."
            elif direction == "left_of_center":
                text += f" The vehicle is positioned slightly left of center ({offset_ratio:.1f}% offset)."
            else:
                text += f" The vehicle is positioned slightly right of center ({offset_ratio:.1f}% offset)."

            # Thêm thông tin khoảng cách đến boundaries
            if offset["dist_from_left_boundary"] is not None and offset["dist_from_right_boundary"] is not None:
                left_dist = offset["dist_from_left_boundary"]
                right_dist = offset["dist_from_right_boundary"]

                text += f" Distance to left boundary: {left_dist:.1f} pixels, distance to right boundary: {right_dist:.1f} pixels."

                # Thông báo nếu xe gần boundary
                min_dist = min(left_dist, right_dist)
                if min_dist < 30:
                    boundary_side = "left" if left_dist < right_dist else "right"
                    text += f" WARNING: Vehicle is close to the {boundary_side} boundary!"
                elif min_dist < 50:
                    boundary_side = "left" if left_dist < right_dist else "right"
                    text += f" Caution: Vehicle is approaching the {boundary_side} boundary."

        return text

    def generate_detailed(self, scene, road_info, lane_info=None):
        """
        Generate detailed scene description với thêm context về các lane.

        Args:
            scene: scene representation
            road_info: road type inference result
            lane_info: danh sách các lane đã classify

        Returns:
            string: mô tả chi tiết cảnh giao thông
        """
        text = self.generate(scene, road_info)

        # Thêm thông tin chi tiết về cấu trúc đường
        total = scene.get("total_lane_lines", 0)
        same = scene.get("same_direction_lanes", 0)
        opposite = scene.get("opposite_direction_lanes", 0)

        text += f"\n\nDetailed road structure: {same} lane(s) same direction + {opposite} lane(s) opposite direction = {total} total lane lines detected in image."

        return text