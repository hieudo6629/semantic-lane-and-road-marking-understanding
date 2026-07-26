import numpy as np


class LaneReasoner:
    """
    Ego-centric, topology-based lane reasoning.

    Key principles:
    1. All lane boundaries visible on camera belong to the same road
    2. The ego lane is defined by two adjacent lane boundaries (left + right)
    3. Other visible lanes are neighbors (left-neighbor or right-neighbor)
    4. We DON'T classify lanes as "same/opposite direction" based on image center
    5. Direction inference comes from spatial grouping/separators, not position

    The system finds the adjacent lane pair that best represents the ego vehicle's lane
    by examining the geometry at the bottom of the image (where the vehicle is).
    """

    def __init__(self, vehicle_position_y_ratio=0.95):
        """
        Args:
            vehicle_position_y_ratio: y-position of vehicle as ratio of image height
                                     (0.95 = near bottom, 1.0 = very bottom)
        """
        self.vehicle_position_y_ratio = vehicle_position_y_ratio

    def analyze(self, lanes, image_width, image_height):
        """
        Main entry point for lane reasoning.

        Args:
            lanes: list of lane points, each lane is [(x1,y1), (x2,y2), ...]
            image_width: image width in pixels
            image_height: image height in pixels

        Returns:
            dict with complete lane reasoning results
        """
        if not lanes:
            return self._empty_result()

        # Step 1: Sort lanes by x-position at vehicle level (bottom of image)
        sorted_lanes = self._sort_lanes_by_x(lanes, image_height)

        # Step 2: Find the ego lane (adjacent pair)
        ego_lane_info = self._find_ego_lane_pair(
            sorted_lanes, image_width, image_height
        )

        # Step 3: Classify all lanes relative to ego lane
        lane_classification = self._classify_all_lanes(
            sorted_lanes, ego_lane_info
        )

        # Step 4: Calculate vehicle offset
        offset_info = self._calculate_vehicle_offset(
            sorted_lanes, ego_lane_info, image_width, image_height
        )

        # Step 5: Infer road topology
        road_info = self._infer_road_topology(sorted_lanes, image_width, image_height)

        return {
            "sorted_lanes": sorted_lanes,
            "ego_lane": ego_lane_info,
            "lane_classification": lane_classification,
            "vehicle_offset": offset_info,
            "road_topology": road_info,
            "image_width": image_width,
            "image_height": image_height,
        }

    def _sort_lanes_by_x(self, lanes, image_height):
        """
        Sort lanes by x-position at a reference height.
        Uses the y-position near the bottom of the image (where perspective is visible).
        """
        reference_y = int(image_height * self.vehicle_position_y_ratio)

        lane_refs = []
        for i, lane in enumerate(lanes):
            x_at_ref = self._get_x_at_y(lane, reference_y)
            lane_refs.append({
                "original_index": i,
                "points": lane,
                "x_at_reference": x_at_ref,
            })

        # Sort by x-position (left to right)
        lane_refs.sort(key=lambda x: x["x_at_reference"])

        # Re-assign sorted indices
        for sorted_idx, lane in enumerate(lane_refs):
            lane["sorted_index"] = sorted_idx

        return lane_refs

    def _get_x_at_y(self, lane_points, y_target, search_range=30, default=None):
        """
        Get the x-coordinate at a specific y-position.
        Uses interpolation for accuracy.
        """
        if not lane_points:
            return default

        # Find points near the target y
        nearby = [p for p in lane_points if abs(p[1] - y_target) <= search_range]

        if nearby:
            if len(nearby) == 1:
                return nearby[0][0]
            return np.mean([p[0] for p in nearby])

        # Find closest point by y
        closest = min(lane_points, key=lambda p: abs(p[1] - y_target))

        # If closest is very far, return default
        if abs(closest[1] - y_target) > search_range * 2:
            return closest[0] if default is None else default

        return closest[0]

    def _find_ego_lane_pair(self, sorted_lanes, image_width, image_height):
        """
        Find the adjacent lane pair that forms the ego lane.

        Strategy:
        - The ego lane is where the vehicle is driving
        - We look for the adjacent lane pair whose midpoint is closest to image center
        - This works because the ego vehicle's camera is typically aligned with the road

        For n lanes, we have (n-1) possible adjacent pairs.
        Score each pair and pick the best.
        """
        n_lanes = len(sorted_lanes)
        vehicle_x = image_width / 2

        if n_lanes == 1:
            # Only one lane boundary visible
            return {
                "left_boundary_index": None,
                "right_boundary_index": sorted_lanes[0]["original_index"],
                "left_boundary_sorted": None,
                "right_boundary_sorted": 0,
                "ego_lane_center_x": sorted_lanes[0]["x_at_reference"],
                "confidence": 0.5,
                "reason": "only_one_lane_visible"
            }

        if n_lanes == 2:
            # Two lanes = left and right boundaries directly
            # Determine which is left and which is right
            lane_0_x = sorted_lanes[0]["x_at_reference"]
            lane_1_x = sorted_lanes[1]["x_at_reference"]

            lane_center_x = (lane_0_x + lane_1_x) / 2
            dist_to_center = abs(lane_center_x - vehicle_x)

            return {
                "left_boundary_index": sorted_lanes[0]["original_index"],
                "right_boundary_index": sorted_lanes[1]["original_index"],
                "left_boundary_sorted": 0,
                "right_boundary_sorted": 1,
                "ego_lane_center_x": lane_center_x,
                "distance_to_vehicle_center": dist_to_center,
                "confidence": 0.9 if dist_to_center < image_width * 0.3 else 0.6,
                "reason": "two_lanes_define_ego_lane"
            }

        # For 3+ lanes, find the best adjacent pair
        best_pair = None
        best_score = float('inf')

        for i in range(n_lanes - 1):
            left_lane = sorted_lanes[i]
            right_lane = sorted_lanes[i + 1]

            # Calculate lane center
            lane_center_x = (left_lane["x_at_reference"] + right_lane["x_at_reference"]) / 2

            # Score = distance from vehicle center to lane center
            # Lower is better
            dist = abs(lane_center_x - vehicle_x)

            # Bonus: prefer pairs that span the image center
            # A lane pair that has vehicle_x between its boundaries is ideal
            left_x = left_lane["x_at_reference"]
            right_x = right_lane["x_at_reference"]
            if left_x < vehicle_x < right_x:
                dist *= 0.5  # Strong preference for vehicle being between lanes

            # Bonus: prefer plausible lane width (not too narrow, not too wide)
            lane_width = right_x - left_x
            expected_width = image_width * 0.15  # ~15% of image width is typical lane
            width_penalty = abs(lane_width - expected_width) / expected_width
            dist *= (1 + width_penalty * 0.2)

            if dist < best_score:
                best_score = dist
                best_pair = {
                    "left_boundary_index": left_lane["original_index"],
                    "right_boundary_index": right_lane["original_index"],
                    "left_boundary_sorted": i,
                    "right_boundary_sorted": i + 1,
                    "ego_lane_center_x": lane_center_x,
                    "lane_width": lane_width,
                    "left_x": left_x,
                    "right_x": right_x,
                }

        dist_to_center = abs(best_pair["ego_lane_center_x"] - vehicle_x)

        # Calculate confidence based on how centered the lane pair is
        if dist_to_center < image_width * 0.1:
            confidence = 0.95
        elif dist_to_center < image_width * 0.25:
            confidence = 0.8
        elif dist_to_center < image_width * 0.4:
            confidence = 0.6
        else:
            confidence = 0.4

        best_pair["distance_to_vehicle_center"] = dist_to_center
        best_pair["confidence"] = confidence
        best_pair["reason"] = "best_adjacent_pair"

        return best_pair

    def _classify_all_lanes(self, sorted_lanes, ego_lane_info):
        """
        Classify all lanes relative to the ego lane.

        Returns:
            dict with:
            - left_neighbor_indices: lanes to the left of ego lane
            - right_neighbor_indices: lanes to the right of ego lane
            - neighbor_count: total neighboring lanes
        """
        left_boundary_sorted = ego_lane_info["left_boundary_sorted"]
        right_boundary_sorted = ego_lane_info["right_boundary_sorted"]

        left_neighbors = []
        right_neighbors = []

        for lane in sorted_lanes:
            sorted_idx = lane["sorted_index"]

            if sorted_idx < left_boundary_sorted:
                left_neighbors.append(lane["original_index"])
            elif sorted_idx > right_boundary_sorted:
                right_neighbors.append(lane["original_index"])

        return {
            "left_neighbor_indices": left_neighbors,
            "right_neighbor_indices": right_neighbors,
            "left_neighbor_count": len(left_neighbors),
            "right_neighbor_count": len(right_neighbors),
            "total_neighbor_count": len(left_neighbors) + len(right_neighbors),
            "ego_left_boundary_index": ego_lane_info["left_boundary_index"],
            "ego_right_boundary_index": ego_lane_info["right_boundary_index"],
        }

    def _calculate_vehicle_offset(self, sorted_lanes, ego_lane_info, image_width, image_height):
        """
        Calculate vehicle offset from lane center.

        Offset is relative to the ego lane's center point.
        Negative offset = vehicle is left of lane center
        Positive offset = vehicle is right of lane center
        """
        vehicle_x = image_width / 2
        lane_center_x = ego_lane_info["ego_lane_center_x"]
        offset_pixels = vehicle_x - lane_center_x

        # Calculate offset as percentage of lane width
        lane_width = ego_lane_info.get("lane_width", 0)
        if lane_width > 0:
            offset_ratio = (offset_pixels / lane_width) * 100
        else:
            offset_ratio = 0

        # Determine direction
        if abs(offset_pixels) < 10:
            direction = "centered"
        elif offset_pixels > 0:
            direction = "right_of_lane_center"
        else:
            direction = "left_of_lane_center"

        # Calculate distances to boundaries
        left_boundary_x = ego_lane_info.get("left_x", lane_center_x - lane_width/2)
        right_boundary_x = ego_lane_info.get("right_x", lane_center_x + lane_width/2)

        dist_to_left = vehicle_x - left_boundary_x
        dist_to_right = right_boundary_x - vehicle_x

        return {
            "offset_pixels": float(offset_pixels),
            "offset_ratio_percent": float(offset_ratio),
            "direction": direction,
            "vehicle_x": float(vehicle_x),
            "lane_center_x": float(lane_center_x),
            "lane_width": float(lane_width) if lane_width > 0 else None,
            "distance_to_left_boundary": float(dist_to_left),
            "distance_to_right_boundary": float(dist_to_right),
            "is_vehicle_between_boundaries": left_boundary_x < vehicle_x < right_boundary_x,
        }

    def _infer_road_topology(self, sorted_lanes, image_width, image_height):
        """
        Infer road topology from lane geometry.

        For typical urban roads, we assume all visible lanes are same direction.
        We look for:
        - Lane convergence (straight road vs curves)
        - Lane separation patterns
        """
        n_lanes = len(sorted_lanes)

        # Get lane positions at top (horizon) and bottom (vehicle)
        horizon_y = int(image_height * 0.3)  # 30% from top
        bottom_y = int(image_height * 0.9)  # 90% from top

        positions_at_horizon = []
        positions_at_bottom = []

        for lane in sorted_lanes:
            x_horizon = self._get_x_at_y(lane["points"], horizon_y)
            x_bottom = lane["x_at_reference"]
            positions_at_horizon.append(x_horizon)
            positions_at_bottom.append(x_bottom)

        # Analyze convergence (straight vs curve)
        if len(sorted_lanes) >= 2:
            # Calculate convergence ratio
            spread_horizon = max(positions_at_horizon) - min(positions_at_horizon)
            spread_bottom = max(positions_at_bottom) - min(positions_at_bottom)

            if spread_horizon > 0:
                convergence_ratio = spread_bottom / spread_horizon
            else:
                convergence_ratio = 1.0

            # If lanes are parallel (convergence close to 1), road is straight
            if abs(convergence_ratio - 1.0) < 0.2:
                curvature = "straight"
                curvature_score = abs(convergence_ratio - 1.0)
            elif convergence_ratio > 1.2:
                curvature = "converging_left"
                curvature_score = convergence_ratio - 1.0
            elif convergence_ratio < 0.8:
                curvature = "converging_right"
                curvature_score = 1.0 - convergence_ratio
            else:
                curvature = "straight"
                curvature_score = abs(convergence_ratio - 1.0)
        else:
            curvature = "unknown"
            curvature_score = 0.5

        return {
            "curvature": curvature,
            "curvature_score": float(curvature_score),
            "total_visible_lanes": n_lanes,
            "laneline_count": n_lanes,
        }

    def _empty_result(self):
        """Return empty result when no lanes detected."""
        return {
            "sorted_lanes": [],
            "ego_lane": {
                "left_boundary_index": None,
                "right_boundary_index": None,
                "ego_lane_center_x": 0,
                "confidence": 0.0,
                "reason": "no_lanes"
            },
            "lane_classification": {
                "left_neighbor_indices": [],
                "right_neighbor_indices": [],
                "total_neighbor_count": 0,
            },
            "vehicle_offset": {
                "offset_pixels": 0,
                "direction": "unknown",
            },
            "road_topology": {
                "curvature": "unknown",
            },
        }


def reason_lanes(lanes, image_width, image_height):
    """
    Convenience function for lane reasoning.

    Args:
        lanes: list of lane points, each lane is [(x1,y1), (x2,y2), ...]
        image_width: image width in pixels
        image_height: image height in pixels

    Returns:
        dict with reasoning results
    """
    reasoner = LaneReasoner()
    return reasoner.analyze(lanes, image_width, image_height)