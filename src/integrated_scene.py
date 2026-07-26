"""
Integrated Scene Understanding

Kết hợp:
1. Lane reasoning (từ lane_reasoning.py)
2. Traffic sign detection (từ yolo_detector.py)
3. Traffic rules (từ traffic_sign_interpreter.py)

Output: Complete scene representation cho LLM inference
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import numpy as np


@dataclass
class IntegratedScene:
    """
    Complete integrated scene representation.

    Combines lane geometry với traffic sign semantics.
    """
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Lane information
    road_info: Dict = field(default_factory=dict)
    ego_lane: Dict = field(default_factory=dict)
    neighbor_lanes: Dict = field(default_factory=dict)
    vehicle_position: Dict = field(default_factory=dict)

    # Traffic sign information
    detected_signs: List[Dict] = field(default_factory=list)
    traffic_rules: List[Dict] = field(default_factory=list)
    active_speed_limit: Optional[int] = None

    # Combined analysis
    urgent_action: str = "no_action"
    has_critical_warning: bool = False
    recommended_speed: Optional[int] = None

    # Metadata
    confidence: float = 0.0
    is_urban: bool = True
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'scene_id': self.scene_id,
            'timestamp': self.timestamp,
            'road': {
                'type': self.road_info.get('type', 'unknown'),
                'curvature': self.road_info.get('curvature', 'unknown'),
                'lane_count': self.road_info.get('lane_count', 0),
                'environment': self.road_info.get('environment', 'unknown')
            },
            'ego_lane': {
                'left_boundary': self.ego_lane.get('left_boundary'),
                'right_boundary': self.ego_lane.get('right_boundary'),
                'center_x': self.ego_lane.get('center_x'),
                'width': self.ego_lane.get('width')
            },
            'neighbor_lanes': {
                'left_count': self.neighbor_lanes.get('left_count', 0),
                'right_count': self.neighbor_lanes.get('right_count', 0)
            },
            'vehicle_position': {
                'offset_pixels': self.vehicle_position.get('offset_pixels', 0),
                'offset_ratio': self.vehicle_position.get('offset_ratio', 0),
                'between_boundaries': self.vehicle_position.get('between_boundaries', True)
            },
            'traffic_signs': {
                'detected': self.detected_signs,
                'count': len(self.detected_signs),
                'has_critical': self.has_critical_warning,
                'active_speed_limit': self.active_speed_limit
            },
            'traffic_rules': {
                'rules': self.traffic_rules,
                'count': len(self.traffic_rules)
            },
            'driving_recommendation': {
                'urgent_action': self.urgent_action,
                'has_critical_warning': self.has_critical_warning,
                'recommended_speed': self.recommended_speed,
                'reasoning': self._get_reasoning()
            },
            'metadata': {
                'confidence': self.confidence,
                'is_urban': self.is_urban,
                **self.metadata
            }
        }

    def _get_reasoning(self) -> str:
        """Generate brief reasoning string."""
        parts = []

        if self.has_critical_warning:
            for rule in self.traffic_rules:
                if rule.get('priority', 99) <= 1:
                    parts.append(f"CRITICAL: {rule.get('description', 'Unknown')}")
                    break

        if self.urgent_action != "no_action":
            parts.append(f"Action: {self.urgent_action}")

        if self.recommended_speed:
            parts.append(f"Speed: {self.recommended_speed} km/h")

        return ". ".join(parts) if parts else "Proceed with caution"


class IntegratedSceneBuilder:
    """
    Builder kết hợp lane reasoning với sign detection.
    """

    def __init__(self, is_urban: bool = True):
        self.is_urban = is_urban

    def build(
        self,
        lane_reasoning: Dict,
        detected_signs: List,
        traffic_situation: Optional[Dict] = None,
        curvature_analysis: Optional[Dict] = None,
        current_speed: Optional[int] = None
    ) -> IntegratedScene:
        """
        Build integrated scene.

        Args:
            lane_reasoning: Output từ LaneReasoner.analyze()
            detected_signs: Output từ YOLOTrafficSignDetector.detect()
            traffic_situation: Output từ TrafficSignInterpreter.interpret() (optional)
            curvature_analysis: Curvature info (optional)
            current_speed: Current vehicle speed (km/h)

        Returns:
            IntegratedScene object
        """
        scene = IntegratedScene(is_urban=self.is_urban)

        # 1. Extract lane information
        ego = lane_reasoning.get('ego_lane', {})
        classification = lane_reasoning.get('lane_classification', {})
        offset = lane_reasoning.get('vehicle_offset', {})

        scene.ego_lane = {
            'left_boundary': ego.get('left_boundary_index'),
            'right_boundary': ego.get('right_boundary_index'),
            'center_x': ego.get('ego_lane_center_x'),
            'width': ego.get('lane_width')
        }

        scene.neighbor_lanes = {
            'left_count': classification.get('left_neighbor_count', 0),
            'right_count': classification.get('right_neighbor_count', 0)
        }

        scene.vehicle_position = {
            'offset_pixels': offset.get('offset_pixels', 0),
            'offset_ratio': offset.get('offset_ratio_percent', 0) / 100,
            'between_boundaries': offset.get('is_vehicle_between_boundaries', True)
        }

        # 2. Road info
        road_curvature = curvature_analysis.get('classification', 'straight') if curvature_analysis else 'unknown'
        scene.road_info = {
            'type': 'urban' if self.is_urban else 'highway',
            'curvature': road_curvature,
            'lane_count': len(lane_reasoning.get('sorted_lanes', [])),
            'environment': 'urban' if self.is_urban else 'highway'
        }

        # 3. Traffic signs
        # Convert DetectedSign objects to dicts if needed
        converted_signs = []
        for s in detected_signs:
            if hasattr(s, 'to_dict'):
                converted_signs.append(s.to_dict())
            elif isinstance(s, dict):
                converted_signs.append(s)
            else:
                converted_signs.append({'sign_type': str(s), 'confidence': 0.5})

        scene.detected_signs = converted_signs

        # 4. Traffic rules
        if traffic_situation:
            scene.traffic_rules = traffic_situation.get('rules', [])
            scene.active_speed_limit = traffic_situation.get('active_speed_limit')

            # Urgent action
            for rule in scene.traffic_rules:
                if rule.get('priority', 99) <= 1:
                    scene.urgent_action = rule.get('action_required', 'no_action')
                    scene.has_critical_warning = True
                    break
            else:
                if scene.traffic_rules:
                    scene.urgent_action = scene.traffic_rules[0].get('action_required', 'no_action')

            scene.has_critical_warning = traffic_situation.get('has_critical_sign', False)

        # 5. Recommended speed
        if scene.active_speed_limit:
            if scene.has_critical_warning:
                scene.recommended_speed = 0
            else:
                scene.recommended_speed = scene.active_speed_limit
        elif current_speed:
            scene.recommended_speed = min(current_speed, 50 if self.is_urban else 80)

        # 6. Confidence
        lane_confidence = ego.get('confidence', 0)
        sign_count = len(scene.detected_signs)
        sign_confidence = sum(s.get('confidence', 0) for s in scene.detected_signs) / max(sign_count, 1)
        scene.confidence = (lane_confidence * 0.7 + sign_confidence * 0.3)

        return scene


def create_integrated_scene(
    lane_reasoning: Dict,
    detected_signs: List,
    traffic_situation: Optional[Dict] = None,
    is_urban: bool = True
) -> IntegratedScene:
    """
    Convenience function to create integrated scene.

    Usage:
        scene = create_integrated_scene(
            lane_reasoning=lane_results,
            detected_signs=sign_detections,
            traffic_situation=interpreted_signs
        )
    """
    builder = IntegratedSceneBuilder(is_urban=is_urban)
    return builder.build(
        lane_reasoning=lane_reasoning,
        detected_signs=detected_signs,
        traffic_situation=traffic_situation
    )