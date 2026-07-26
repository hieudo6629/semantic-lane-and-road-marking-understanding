"""
Robust Lane Curvature Estimation

Key Insight:
------------

For parallel lanes in the real world, their vanishing points (VPs) should converge
to approximately the same location in the image. If lanes have different VPs, the
road might be curved.

Algorithm:
---------

1. For each lane, fit a polynomial and analyze the residuals
2. Compare linear vs quadratic fit quality
3. Use vanishing point consistency and drift analysis
"""

import numpy as np
from typing import List, Tuple, Optional, Dict


class LaneCurvatureEstimator:
    """
    Estimates lane curvature using polynomial analysis and vanishing point consistency.
    """

    def __init__(self):
        pass

    def estimate(
        self,
        lane_points: List[Tuple[float, float]],
        image_width: int,
        image_height: int
    ) -> Dict:
        """
        Estimate curvature for a single lane.
        """
        if len(lane_points) < 4:
            return self._insufficient_data()

        points = np.array(lane_points)

        # Validate
        valid_mask = (points[:, 0] > 0) & (points[:, 0] < image_width) & \
                     (points[:, 1] > 0) & (points[:, 1] < image_height)
        points = points[valid_mask]

        if len(points) < 4:
            return self._insufficient_data()

        # Sort by y (depth, top to bottom)
        sorted_idx = np.argsort(points[:, 1])
        points = points[sorted_idx]

        return self._analyze_lane_curvature(points)

    def _analyze_lane_curvature(self, points: np.ndarray) -> Dict:
        """
        Analyze a single lane for curvature.

        Returns vanishing point and curvature metrics.
        """
        try:
            y_vals = points[:, 1]
            x_vals = points[:, 0]

            # Normalize y to [0, 1] for numerical stability
            y_min, y_max = np.min(y_vals), np.max(y_vals)
            y_norm = (y_vals - y_min) / max(y_max - y_min, 1)

            # Fit linear and quadratic models
            try:
                coeffs_linear = np.polyfit(y_norm, x_vals, deg=1)
                x_pred_linear = np.polyval(coeffs_linear, y_norm)
                mse_linear = np.mean((x_vals - x_pred_linear) ** 2)
            except:
                mse_linear = float('inf')

            try:
                coeffs_quad = np.polyfit(y_norm, x_vals, deg=2)
                x_pred_quad = np.polyval(coeffs_quad, y_norm)
                mse_quad = np.mean((x_vals - x_pred_quad) ** 2)
            except:
                mse_quad = float('inf')

            # Vanishing point approximation
            # At y_norm = 1 (bottom), x = a + b + c
            # At y_norm = 0 (top), x = c
            if len(coeffs_quad) >= 3:
                vp_x = coeffs_quad[2]  # x at top of normalized range
            else:
                vp_x = x_vals[0]

            # Compute drift ratio (how much lane deviates from straight perspective)
            if mse_linear > 0:
                improvement = (mse_linear - mse_quad) / mse_linear
            else:
                improvement = 0

            # Key metric: drift
            # For perspective convergence on straight road: MSE ~ 0 (after linear fit)
            # For curved road: MSE will be higher even after quadratic fit
            drift_ratio = np.sqrt(mse_linear) / max(image_width, 1)

            return {
                'vanishing_point': (float(vp_x), 0.0),
                'mse_linear': float(mse_linear),
                'mse_quadratic': float(mse_quad),
                'fit_improvement': float(improvement),
                'drift_ratio': float(drift_ratio),
                'is_straight': mse_linear < 1000,  # Threshold
                'confidence': 0.7 if mse_linear < 1000 else 0.5
            }

        except Exception:
            return self._insufficient_data()

    def _insufficient_data(self) -> Dict:
        return {
            'vanishing_point': None,
            'is_straight': True,
            'confidence': 0.3
        }


def batch_estimate_curvature(
    lanes: List[List[Tuple[float, float]]],
    image_width: int,
    image_height: int
) -> List[Dict]:
    """Estimate curvature for multiple lanes."""
    estimator = LaneCurvatureEstimator()
    results = []
    for lane in lanes:
        result = estimator.estimate(lane, image_width, image_height)
        results.append(result)
    return results


def aggregate_curvature(
    lane_curvatures: List[Dict],
    lanes: Optional[List[List[List[float]]]] = None,
    image_width: int = 1640,
    image_height: int = 590
) -> Dict:
    """
    Aggregate curvature from multiple lanes.

    For straight roads, lanes should have:
    1. Similar vanishing points
    2. Small drift ratios
    3. Consistent linear fit quality
    """
    if not lane_curvatures:
        return _empty_result()

    # Collect metrics
    vps = []
    drift_ratios = []
    straight_count = 0

    for c in lane_curvatures:
        vp = c.get('vanishing_point')
        if vp:
            vps.append(vp[0])  # Store x coordinate only
        drift_ratios.append(c.get('drift_ratio', 0))
        if c.get('is_straight', False):
            straight_count += 1

    # Analyze vanishing point spread
    if len(vps) >= 2:
        vp_spread = max(vps) - min(vps)
        avg_vp = np.mean(vps)
    else:
        vp_spread = 0
        avg_vp = image_width / 2

    # Analyze drift
    avg_drift = np.mean(drift_ratios) if drift_ratios else 0

    # Determine direction from lane positions
    direction = _analyze_direction(lanes, image_width, image_height) if lanes else 'straight'

    # Classification
    # Straight road: low VP spread, low drift, most lanes appear straight
    straight_ratio = straight_count / len(lane_curvatures) if lane_curvatures else 0

    if vp_spread < 50 and avg_drift < 0.1 and straight_ratio > 0.5:
        # Tight VP clustering + low drift = straight road
        classification = 'straight'
        confidence = min(0.9, 0.6 + straight_ratio * 0.3)
        curvature_magnitude = vp_spread / 1000
    elif vp_spread > 200 or avg_drift > 0.3:
        # High spread or high drift = curved road
        classification = f'sharp_{direction}_curve' if direction != 'straight' else 'sharp_curve'
        confidence = 0.7
        curvature_magnitude = (vp_spread + avg_drift * 1000) / 100
    else:
        # Moderate = gentle curve
        classification = f'gentle_{direction}_curve' if direction != 'straight' else 'gentle_curve'
        confidence = 0.6
        curvature_magnitude = (vp_spread + avg_drift * 500) / 500

    return {
        'curvature_magnitude': float(curvature_magnitude),
        'direction': direction,
        'classification': classification,
        'confidence': float(confidence),
        'vanishing_point_spread': float(vp_spread),
        'avg_drift': float(avg_drift),
        'straight_ratio': float(straight_ratio),
        'lane_curvatures': lane_curvatures
    }


def _analyze_direction(
    lanes: Optional[List[List[List[float]]]],
    image_width: int,
    image_height: int
) -> str:
    """
    Analyze overall road direction from lane positions.

    For straight roads, lane x-positions should change linearly with depth.
    For curved roads, the x-position change is non-linear.
    """
    if not lanes or len(lanes) < 2:
        return 'straight'

    try:
        y_bottom = int(image_height * 0.85)
        y_top = int(image_height * 0.35)

        x_shifts = []

        for lane in lanes:
            lane_array = np.array(lane)
            valid = (lane_array[:, 0] > 0) & (lane_array[:, 1] > 0)
            lane_array = lane_array[valid]

            if len(lane_array) < 3:
                continue

            # Get x at bottom and top
            bottom_pts = lane_array[np.abs(lane_array[:, 1] - y_bottom) < 80]
            top_pts = lane_array[np.abs(lane_array[:, 1] - y_top) < 80]

            if len(bottom_pts) > 0 and len(top_pts) > 0:
                x_bottom = np.mean(bottom_pts[:, 0])
                x_top = np.mean(top_pts[:, 0])
                shift = x_bottom - x_top
                x_shifts.append(shift)

        if not x_shifts:
            return 'straight'

        avg_shift = np.mean(x_shifts)

        # Normalize by image width
        shift_ratio = avg_shift / image_width

        # Determine direction
        if abs(shift_ratio) < 0.08:
            return 'straight'
        elif shift_ratio > 0:
            return 'right'  # Lanes shift right = road curves right
        else:
            return 'left'

    except Exception:
        return 'straight'


def _empty_result() -> Dict:
    return {
        'curvature_magnitude': 0,
        'direction': 'unknown',
        'classification': 'unknown',
        'confidence': 0.0
    }


# Direct test
if __name__ == "__main__":
    example_lanes = [
        [(-16.44, 580), (22.27, 570), (50.12, 560), (100.35, 540),
         (180.55, 510), (280.42, 470), (400.15, 420), (520.33, 380),
         (620.50, 350), (681.38, 400)],
        [(533.50, 590), (542.95, 580), (562.30, 560), (592.15, 530),
         (642.30, 490), (712.25, 440), (762.85, 390), (733.45, 400)],
        [(1186.93, 590), (1166.92, 580), (1106.50, 550), (1020.30, 510),
         (920.15, 460), (850.45, 410), (773.33, 400)],
        [(1668.99, 550), (1613.13, 540), (1520.50, 500), (1400.25, 450),
         (1280.40, 400), (1150.60, 360), (825.60, 400)],
    ]

    results = batch_estimate_curvature(example_lanes, 1640, 590)
    agg = aggregate_curvature(results, example_lanes, 1640, 590)

    print("Per-lane analysis:")
    for i, r in enumerate(results):
        vp = r.get('vanishing_point')
        vp_str = f"{vp[0]:.1f}" if vp and vp[0] is not None else "N/A"
        drift = r.get('drift_ratio', 0)
        print(f"  Lane {i}: VP_x={vp_str}, drift={drift:.4f}" if drift else f"  Lane {i}: VP_x={vp_str}")

    print(f"\nAggregated: {agg['classification']}")
    print(f"  Direction: {agg['direction']}")
    print(f"  VP spread: {agg.get('vanishing_point_spread', 0):.1f}")
    print(f"  Confidence: {agg['confidence']:.2f}")