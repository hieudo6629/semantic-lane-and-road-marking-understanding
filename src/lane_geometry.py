import numpy as np


class LaneGeometry:

    def __init__(self):
        pass

    def fit_lane_polynomial(self, lane_points):

        xs = [p[0] for p in lane_points]
        ys = [p[1] for p in lane_points]

        xs = np.array(xs)
        ys = np.array(ys)

        # fit x = ay^2 + by + c
        coeffs = np.polyfit(ys, xs, 2)

        a, b, c = coeffs

        return {
            "a": float(a),
            "b": float(b),
            "c": float(c)
        }

    def compute_curvature(self, coeffs, y_eval):

        a = coeffs["a"]
        b = coeffs["b"]

        # curvature formula
        curvature = ((1 + (2*a*y_eval + b)**2)**1.5) / abs(2*a + 1e-6)

        return float(curvature)

    def process_lanes(self, lanes, image_height):

        results = []

        y_eval = image_height

        for lane in lanes:

            coeffs = self.fit_lane_polynomial(lane)

            curvature = self.compute_curvature(coeffs, y_eval)

            lane_info = {
                "coefficients": coeffs,
                "curvature": curvature
            }

            results.append(lane_info)

        return results