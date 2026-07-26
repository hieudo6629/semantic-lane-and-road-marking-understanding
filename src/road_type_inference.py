"""
Road Type Inference

Infers semantic road type from lane geometry.

Output types:
- straight
- gentle_left_curve
- sharp_left_curve
- gentle_right_curve
- sharp_right_curve
- T-junction
- intersection

Environmental inference (optional):
- urban road
- highway
- narrow road
"""

import numpy as np
from typing import List, Dict, Optional
from lane_curvature import LaneCurvatureEstimator, aggregate_curvature


class RoadTypeInference:
    """
    Ego-centric road type inference.

    Uses curvature analysis and road geometry to classify road type.
    """

    # Curvature thresholds for road classification
    CURVE_THRESHOLD_GENTLE = 2e-4
    CURVE_THRESHOLD_SHARP = 5e-4

    # Lane width thresholds (pixels, normalized)
    NARROW_ROAD_WIDTH = 150
    WIDE_ROAD_WIDTH = 400

    def __init__(self):
        self.curvature_estimator = LaneCurvatureEstimator()

    def infer(
        self,
        lanes: List[List],
        ego_lane_info: Dict,
        image_width: int,
        image_height: int,
        lane_curvatures: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Infer road type from lane data.

        Args:
            lanes: List of lane point lists
            ego_lane_info: Ego lane detection results
            image_width: Image width
            image_height: Image height
            lane_curvatures: Pre-computed curvatures (optional)

        Returns:
            Dict with road type inference
        """
        if not lanes:
            return self._empty_result()

        # Compute curvature if not provided
        if lane_curvatures is None:
            lane_curvatures = self._compute_curvatures(lanes, image_width, image_height)

        # Aggregate curvature across lanes
        aggregated = aggregate_curvature(lane_curvatures)

        # Analyze lane geometry
        geometry_analysis = self._analyze_road_geometry(lanes, ego_lane_info, image_width, image_height)

        # Combine analyses
        road_type = self._classify_road_type(aggregated, geometry_analysis)
        road_environment = self._infer_environment(geometry_analysis, ego_lane_info)

        return {
            'road_type': road_type,
            'road_environment': road_environment,
            'curvature': aggregated['curvature_magnitude'],
            'curvature_direction': aggregated['direction'],
            'curvature_confidence': aggregated['confidence'],
            'classification': aggregated['classification'],
            'geometry': geometry_analysis,
            'details': {
                'aggregated_curvature': aggregated,
                'lane_curvatures': lane_curvatures
            }
        }

    def _compute_curvatures(self, lanes, image_width, image_height) -> List[Dict]:
        """Compute curvature for each lane."""
        curvatures = []
        for lane_points in lanes:
            curv = self.curvature_estimator.estimate(lane_points, image_width, image_height)
            curvatures.append(curv)
        return curvatures

    def _analyze_road_geometry(self, lanes, ego_lane_info, image_width, image_height) -> Dict:
        """Analyze road geometry for type inference."""
        y_eval = int(image_height * 0.95)  # Near bottom of image

        # Get lane positions
        lane_x_at_bottom = []
        for lane_points in lanes:
            nearby = [(p[0], p[1]) for p in lane_points if abs(p[1] - y_eval) < 50]
            if nearby:
                x = np.mean([p[0] for p in nearby])
                lane_x_at_bottom.append(x)

        if not lane_x_at_bottom:
            return {'geometry_type': 'unknown'}

        # Analyze lane spread
        spread = max(lane_x_at_bottom) - min(lane_x_at_bottom) if lane_x_at_bottom else 0
        coverage_ratio = spread / image_width if image_width > 0 else 0

        # Check if lanes are converging or diverging
        y_top = int(image_height * 0.3)
        lane_x_at_top = []
        for lane_points in lanes:
            nearby = [(p[0], p[1]) for p in lane_points if abs(p[1] - y_top) < 50]
            if nearby:
                x = np.mean([p[0] for p in nearby])
                lane_x_at_top.append(x)

        convergence_ratio = 0
        if len(lane_x_at_bottom) >= 2 and len(lane_x_at_top) >= 2:
            spread_top = max(lane_x_at_top) - min(lane_x_at_top)
            spread_bottom = max(lane_x_at_bottom) - min(lane_x_at_bottom)
            if spread_top > 0:
                convergence_ratio = spread_bottom / spread_top

        # Determine if road has multiple lanes visible
        lane_count = len(lanes)

        # Classify geometry pattern
        if coverage_ratio < 0.3:
            geometry_type = 'narrow'
        elif coverage_ratio < 0.6:
            geometry_type = 'single_lane_view'  # Single lane direction
        else:
            geometry_type = 'multi_lane'

        return {
            'spread_pixels': float(spread),
            'coverage_ratio': float(coverage_ratio),
            'convergence_ratio': float(convergence_ratio),
            'lane_count': lane_count,
            'geometry_type': geometry_type
        }

    def _classify_road_type(self, curvature_agg: Dict, geometry: Dict) -> str:
        """Classify road type based on curvature and geometry."""
        curvature = curvature_agg.get('curvature_magnitude', 0)
        direction = curvature_agg.get('direction', 'straight')
        confidence = curvature_agg.get('confidence', 0)

        # If low confidence or near straight threshold, classify as straight
        if confidence < 0.4 or curvature < self.CURVE_THRESHOLD_GENTLE * 0.5:
            return 'straight'

        # Classify by curvature intensity
        if curvature < self.CURVE_THRESHOLD_GENTLE:
            return 'straight'
        elif curvature < self.CURVE_THRESHOLD_SHARP:
            return f'gentle_{direction}_curve' if direction != 'straight' else 'straight'
        else:
            return f'sharp_{direction}_curve' if direction != 'straight' else 'straight'

    def _infer_environment(self, geometry: Dict, ego_lane_info: Dict) -> str:
        """Infer road environment type."""
        geometry_type = geometry.get('geometry_type', 'single_lane_view')
        coverage = geometry.get('coverage_ratio', 0.5)
        lane_count = geometry.get('lane_count', 1)

        if geometry_type == 'narrow':
            return 'narrow_road'
        elif lane_count >= 4 and coverage > 0.5:
            return 'urban_marketplace'
        elif lane_count >= 3:
            return 'urban_multi_lane'
        elif lane_count <= 2:
            return 'highway' if coverage > 0.4 else 'rural_road'
        else:
            return 'urban_road'

    def _empty_result(self) -> Dict:
        """Return empty result."""
        return {
            'road_type': 'unknown',
            'road_environment': 'unknown',
            'curvature': 0,
            'curvature_direction': 'unknown',
            'confidence': 0.0,
            'classification': 'unknown',
            'geometry': {}
        }


def interpret_road_type(road_type: str) -> str:
    """
    Provide human-readable interpretation of road type.

    Useful for debugging and scene description.
    """
    interpretations = {
        'straight': 'The road continues straight ahead with minimal curvature.',
        'gentle_left_curve': 'The road curves gently toward the left.',
        'gentle_right_curve': 'The road curves gently toward the right.',
        'sharp_left_curve': 'The road takes a sharp turn to the left.',
        'sharp_right_curve': 'The road takes a sharp turn to the right.',
        'sharp_curve': 'The road contains a sharp curve.',
        'narrow_road': 'This appears to be a narrow single-lane road.',
        'urban_road': 'This is an urban road with multiple lanes.',
        'highway': 'This appears to be a highway or similar wide road.',
        'rural_road': 'This is likely a rural or countryside road.',
    }
    return interpretations.get(road_type, road_type)