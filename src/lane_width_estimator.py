import numpy as np


class LaneWidthEstimator:

    def __init__(self):
        pass

    def estimate(self, lanes, ego_lane_info, image_height):

        left_idx = ego_lane_info["left_boundary"]
        right_idx = ego_lane_info["right_boundary"]

        if left_idx is None or right_idx is None:
            return None

        left_lane = lanes[left_idx]
        right_lane = lanes[right_idx]

        # lấy điểm gần bottom image
        left_bottom = max(left_lane, key=lambda p: p[1])
        right_bottom = max(right_lane, key=lambda p: p[1])

        lane_width = abs(right_bottom[0] - left_bottom[0])

        return {
            "lane_width_pixels": float(lane_width),
            "left_point": left_bottom,
            "right_point": right_bottom
        }