import numpy as np


class EgoLaneDetector:

    def __init__(self):
        pass

    def detect(self, lane_info, image_width):

        center_x = image_width / 2

        # Tìm lane gần center nhất
        min_dist = float("inf")
        ego_lane_idx = None

        for i, lane in enumerate(lane_info):

            mean_x = lane["mean_x"]
            dist = abs(mean_x - center_x)

            if dist < min_dist:
                min_dist = dist
                ego_lane_idx = i

        left_boundary = None
        right_boundary = None

        if ego_lane_idx is not None:

            if ego_lane_idx > 0:
                left_boundary = ego_lane_idx - 1

            if ego_lane_idx < len(lane_info) - 1:
                right_boundary = ego_lane_idx + 1

        result = {
            "ego_lane_index": ego_lane_idx,
            "left_boundary": left_boundary,
            "right_boundary": right_boundary
        }

        return result