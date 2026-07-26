"""
Driving Corridor Visualization

Visualizes:
1. Ego lane area
2. Lane center
3. Vehicle position and offset
4. Neighboring lanes
5. Drivable corridor

OpenCV-based visualization for analysis and thesis figures.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import cv2


# Color definitions (BGR format for OpenCV)
COLORS = {
    'ego_lane': (0, 255, 0),       # Bright green
    'ego_lane_fill': (0, 100, 0),   # Dark green
    'left_neighbor': (255, 165, 0), # Orange
    'right_neighbor': (255, 165, 0),  # Orange
    'lane_center': (0, 255, 255),  # Yellow
    'vehicle': (0, 0, 255),        # Red
    'text': (255, 255, 255),       # White
    'background': (40, 40, 40),     # Dark gray
    'grid': (80, 80, 80),           # Gray
    'horizon': (100, 150, 255),     # Light blue
}


class CorridorVisualizer:
    """
    Visualizes driving corridor and lane information.

    Supports:
    - Overlaying lane boundaries
    - Filling ego lane area
    - Drawing lane centers
    - Marking vehicle position
    - Adding informational text
    """

    def __init__(self, image_width: int = 1640, image_height: int = 590):
        self.image_width = image_width
        self.image_height = image_height

    def visualize(
        self,
        image: Optional[np.ndarray],
        lanes: List[List[Tuple[float, float]]],
        ego_lane_info: Dict,
        vehicle_offset: Dict,
        sorted_lanes: Optional[List[Dict]] = None,
        show_annotations: bool = True,
        show_vehicle: bool = True,
        show_center_line: bool = True
    ) -> np.ndarray:
        """
        Create complete visualization.

        Args:
            image: Original image (will be copied) or None for blank canvas
            lanes: List of lane point lists
            ego_lane_info: Ego lane detection results
            vehicle_offset: Vehicle offset results
            sorted_lanes: Sorted lane info from reasoner
            show_annotations: Show text annotations
            show_vehicle: Show vehicle marker
            show_center_line: Show lane center line

        Returns:
            Visualization image
        """
        if image is None:
            vis = np.full((self.image_height, self.image_width, 3), 40, dtype=np.uint8)
        else:
            vis = image.copy()
            if len(vis.shape) == 2:
                vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

        # Draw lane boundaries
        self._draw_lanes(vis, lanes, sorted_lanes)

        # Fill ego lane area
        self._fill_ego_lane(vis, lanes, ego_lane_info)

        # Draw lane center
        if show_center_line:
            self._draw_lane_center(vis, lanes, ego_lane_info)

        # Draw vehicle marker
        if show_vehicle:
            self._draw_vehicle(vis, vehicle_offset)

        # Draw lane labels
        if show_annotations:
            self._draw_annotations(vis, lanes, ego_lane_info, vehicle_offset)

        return vis

    def _draw_lanes(
        self,
        vis: np.ndarray,
        lanes: List[List[Tuple[float, float]]],
        sorted_lanes: Optional[List[Dict]] = None
    ):
        """Draw all lane boundaries."""
        for i, lane_points in enumerate(lanes):
            if not lane_points:
                continue

            pts = np.array(lane_points, dtype=np.int32)
            if len(pts) < 2:
                continue

            # Determine color based on position
            color = (150, 150, 150)  # Default gray
            thickness = 2

            if sorted_lanes:
                ego = None
                if 'ego_lane' in sorted_lanes[i] if isinstance(sorted_lanes[i], dict) else False:
                    # Lane is part of ego
                    color = COLORS['ego_lane']
                    thickness = 3
            else:
                # Default styling
                color = (200, 200, 200)
                thickness = 2

            cv2.polylines(vis, [pts], isClosed=False, color=color, thickness=thickness)

    def _fill_ego_lane(
        self,
        vis: np.ndarray,
        lanes: List[List[Tuple[float, float]]],
        ego_lane_info: Dict
    ):
        """Fill the ego lane area with semi-transparent color."""
        left_idx = ego_lane_info.get('left_boundary_index')
        right_idx = ego_lane_info.get('right_boundary_index')

        if left_idx is None or right_idx is None:
            return
        if left_idx >= len(lanes) or right_idx >= len(lanes):
            return

        left_lane = lanes[left_idx]
        right_lane = lanes[right_idx]

        if not left_lane or not right_lane:
            return

        # Create polygon for ego lane fill
        # Use left boundary points (top to bottom) + reversed right boundary points
        left_pts = sorted(left_lane, key=lambda p: -p[1])  # Top to bottom
        right_pts = sorted(right_lane, key=lambda p: -p[1])  # Top to bottom

        # Create filled polygon
        fill_pts = []
        for pt in left_pts:
            fill_pts.append([pt[0], pt[1]])
        for pt in right_pts:
            fill_pts.append([pt[0], pt[1]])

        if len(fill_pts) > 2:
            fill_array = np.array([fill_pts], dtype=np.int32)
            overlay = vis.copy()
            cv2.fillPoly(overlay, fill_array, COLORS['ego_lane_fill'])
            cv2.addWeighted(vis, 0.7, overlay, 0.3, 0, vis)

    def _draw_lane_center(
        self,
        vis: np.ndarray,
        lanes: List[List[Tuple[float, float]]],
        ego_lane_info: Dict
    ):
        """Draw the center line of the ego lane."""
        left_idx = ego_lane_info.get('left_boundary_index')
        right_idx = ego_lane_info.get('right_boundary_index')

        if left_idx is None or right_idx is None:
            return
        if left_idx >= len(lanes) or right_idx >= len(lanes):
            return

        left_lane = lanes[left_idx]
        right_lane = lanes[right_idx]

        # Sample points at same y-level
        sample_y = int(self.image_height * 0.8)  # Near bottom

        left_x = self._get_x_at_y(left_lane, sample_y)
        right_x = self._get_x_at_y(right_lane, sample_y)

        if left_x is None or right_x is None:
            return

        center_x = (left_x + right_x) / 2

        # Draw vertical center line
        cv2.line(
            vis,
            (int(center_x), sample_y),
            (int(center_x), int(sample_y * 0.5)),
            COLORS['lane_center'],
            2,
            cv2.LINE_AA
        )

    def _draw_vehicle(
        self,
        vis: np.ndarray,
        vehicle_offset: Dict
    ):
        """Draw vehicle position marker."""
        vehicle_x = vehicle_offset.get('vehicle_x', self.image_width / 2)
        vehicle_y = int(self.image_height * 0.95)

        # Draw vehicle rectangle
        width = 60
        height = 30
        top_left = (int(vehicle_x - width/2), int(vehicle_y - height/2))
        bottom_right = (int(vehicle_x + width/2), int(vehicle_y + height/2))

        cv2.rectangle(vis, top_left, bottom_right, COLORS['vehicle'], -1)
        cv2.rectangle(vis, top_left, bottom_right, (255, 255, 255), 2)

        # Draw direction arrow
        arrow_start = (int(vehicle_x), int(vehicle_y))
        arrow_end = (int(vehicle_x), int(vehicle_y - 40))
        cv2.arrowedLine(vis, arrow_start, arrow_end, (255, 255, 255), 2, tipLength=0.3)

    def _draw_annotations(
        self,
        vis: np.ndarray,
        lanes: List[List[Tuple[float, float]]],
        ego_lane_info: Dict,
        vehicle_offset: Dict
    ):
        """Draw text annotations."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 30

        # Lane info
        text = f"Ego Lanes: {ego_lane_info.get('left_boundary_index', '?')}-{ego_lane_info.get('right_boundary_index', '?')}"
        cv2.putText(vis, text, (20, y_offset), font, 0.6, COLORS['text'], 1)
        y_offset += 25

        # Offset info
        offset = vehicle_offset.get('offset_pixels', 0)
        direction = vehicle_offset.get('direction', 'unknown')
        text = f"Offset: {offset:.1f} px ({direction})"
        cv2.putText(vis, text, (20, y_offset), font, 0.6, COLORS['text'], 1)
        y_offset += 25

        # Lane boundaries
        left_neighbor = lane_classification.get('left_neighbor_count', 0) if (lane_classification := ego_lane_info.get('lane_classification', {})) else 0
        right_neighbor = lane_classification.get('right_neighbor_count', 0) if lane_classification else 0
        text = f"Left neighbors: {left_neighbor}, Right neighbors: {right_neighbor}"
        cv2.putText(vis, text, (20, y_offset), font, 0.6, COLORS['text'], 1)

    def _get_x_at_y(self, lane_points: List[Tuple[float, float]], y_target: int, search_range: int = 30) -> Optional[float]:
        """Get x coordinate at specific y position."""
        if not lane_points:
            return None

        nearby = [(p[0], p[1]) for p in lane_points if abs(p[1] - y_target) <= search_range]

        if nearby:
            return np.mean([p[0] for p in nearby])

        closest = min(lane_points, key=lambda p: abs(p[1] - y_target))
        if abs(closest[1] - y_target) <= search_range * 2:
            return closest[0]

        return None


def create_thesis_figure(
    image: np.ndarray,
    lanes: List[List[Tuple[float, float]]],
    ego_lane_info: Dict,
    vehicle_offset: Dict,
    title: str = "Driving Corridor Visualization"
) -> np.ndarray:
    """
    Create publication-ready figure for thesis.

    Higher quality output with better spacing and labels.
    """
    vis = image.copy()
    if len(vis.shape) == 2:
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    visualizer = CorridorVisualizer(vis.shape[1], vis.shape[0])
    return visualizer.visualize(
        vis, lanes, ego_lane_info, vehicle_offset,
        show_annotations=True,
        show_vehicle=True,
        show_center_line=True
    )