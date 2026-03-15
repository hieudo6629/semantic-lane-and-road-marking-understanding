class SceneBuilder:

    def __init__(self):
        pass

    def build(self, lane_info, ego_lane, lane_geometry, lane_width):

        scene = {}

        scene["lane_count"] = len(lane_info)

        scene["ego_lane"] = {
            "index": ego_lane["ego_lane_index"],
            "left_boundary": ego_lane["left_boundary"],
            "right_boundary": ego_lane["right_boundary"]
        }

        if lane_width is not None:
            scene["lane_width_pixels"] = lane_width["lane_width_pixels"]

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

        return scene