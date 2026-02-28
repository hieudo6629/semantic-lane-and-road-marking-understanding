import numpy as np

class LaneStructureBuilder:

    def build(self, image, lanes):
        h, w, _ = image.shape

        lane_count = len(lanes)

        center_x = w / 2
        ego_lane = self._find_closest_lane(lanes, center_x)

        structure = {
            "lanes": {
                "count": lane_count,
                "ego_lane_index": ego_lane
            },
            "road_markings": {
                "merge_ahead": False,
                "crosswalk": False
            }
        }

        return structure

    def _find_closest_lane(self, lanes, center_x):
        min_dist = 1e9
        ego_index = -1

        for i, lane in enumerate(lanes):
            xs = [p[0] for p in lane]
            avg_x = np.mean(xs)
            dist = abs(avg_x - center_x)

            if dist < min_dist:
                min_dist = dist
                ego_index = i

        return ego_index