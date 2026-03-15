class RoadInference:

    def __init__(self):
        pass

    def infer(self, lane_geometry, ego_lane):

        ego_idx = ego_lane["ego_lane_index"]

        coeffs = lane_geometry[ego_idx]["coefficients"]

        a = coeffs["a"]

        threshold = 1e-4

        if abs(a) < threshold:
            road_type = "straight"
        elif a > 0:
            road_type = "left_curve"
        else:
            road_type = "right_curve"

        return {
            "road_type": road_type,
            "a": a
        }