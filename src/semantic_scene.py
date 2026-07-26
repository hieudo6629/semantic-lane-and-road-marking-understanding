"""
Semantic Scene Representation Builder

Generates hierarchical, LLM-friendly JSON representations of traffic scenes.

Schema Design Principles:
1. Hierarchical: Organized from general (road) to specific (ego lane details)
2. Extensible: Can add new fields without breaking existing consumers
3. LLM-friendly: Clear naming, consistent types, minimal nesting
4. Serializable: Standard JSON with no special types

Target Schema:
{
  "scene_id": "timestamp_uuid",
  "timestamp": "ISO_datetime",
  "road": {...},
  "ego_lane": {...},
  "neighbor_lanes": {...},
  "vehicle_position": {...},
  "lane_semantics": {...},
  "traffic_context": {...},
  "metadata": {...}
}
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import numpy as np


@dataclass
class RoadRepresentation:
    """Road-level information."""
    type: str = "unknown"
    curvature: str = "straight"
    lane_count: int = 0
    width_estimate: Optional[float] = None
    convergence: str = "parallel"  # parallel, converging, diverging
    environment: str = "unknown"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EgoLaneRepresentation:
    """Ego lane information."""
    left_boundary: Optional[int] = None
    right_boundary: Optional[int] = None
    center_x: Optional[float] = None
    width_pixels: Optional[float] = None
    offset_ratio: float = 0.0
    offset_pixels: float = 0.0
    offset_direction: str = "centered"
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NeighborLanesRepresentation:
    """Neighbor lanes information."""
    left_count: int = 0
    right_count: int = 0
    left_indices: List[int] = field(default_factory=list)
    right_indices: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class VehiclePositionRepresentation:
    """Vehicle position relative to lane."""
    x_pixels: float = 0.0
    y_pixels: float = 0.0
    lane_center_offset: float = 0.0
    lane_boundary_distances: Dict[str, float] = field(default_factory=dict)
    is_centered: bool = True
    is_between_boundaries: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LaneSemanticsRepresentation:
    """Lane semantic information."""
    total_lanes: int = 0
    drivable_lanes: int = 0
    ego_lane_index: Optional[int] = None
    lane_details: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrafficContextRepresentation:
    """Traffic context information."""
    visible_lanes: int = 0
    lane_direction_type: str = "single_direction"  # same, mixed, unknown
    confidence: str = "low"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SemanticScene:
    """
    Complete semantic scene representation.

    This is the main output of the scene representation builder.
    """
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    road: RoadRepresentation = field(default_factory=RoadRepresentation)
    ego_lane: EgoLaneRepresentation = field(default_factory=EgoLaneRepresentation)
    neighbor_lanes: NeighborLanesRepresentation = field(default_factory=NeighborLanesRepresentation)
    vehicle_position: VehiclePositionRepresentation = field(default_factory=VehiclePositionRepresentation)
    lane_semantics: LaneSemanticsRepresentation = field(default_factory=LaneSemanticsRepresentation)
    traffic_context: TrafficContextRepresentation = field(default_factory=TrafficContextRepresentation)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "scene_id": self.scene_id,
            "timestamp": self.timestamp,
            "road": self.road.to_dict(),
            "ego_lane": self.ego_lane.to_dict(),
            "neighbor_lanes": self.neighbor_lanes.to_dict(),
            "vehicle_position": self.vehicle_position.to_dict(),
            "lane_semantics": self.lane_semantics.to_dict(),
            "traffic_context": self.traffic_context.to_dict(),
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        import json

        def convert(obj):
            """Convert numpy types to native Python for JSON serialization."""
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj

        return json.dumps(convert(self.to_dict()), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SemanticScene':
        """Create from dictionary."""
        road = RoadRepresentation(**data.get('road', {}))
        ego_lane = EgoLaneRepresentation(**data.get('ego_lane', {}))
        neighbor_lanes = NeighborLanesRepresentation(**data.get('neighbor_lanes', {}))
        vehicle_position = VehiclePositionRepresentation(**data.get('vehicle_position', {}))
        lane_semantics = LaneSemanticsRepresentation(**data.get('lane_semantics', {}))
        traffic_context = TrafficContextRepresentation(**data.get('traffic_context', {}))

        return cls(
            scene_id=data.get('scene_id', str(uuid.uuid4())),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            road=road,
            ego_lane=ego_lane,
            neighbor_lanes=neighbor_lanes,
            vehicle_position=vehicle_position,
            lane_semantics=lane_semantics,
            traffic_context=traffic_context,
            metadata=data.get('metadata', {})
        )


class SemanticSceneBuilder:
    """
    Builds semantic scene representations from lane analysis results.

    This builder aggregates outputs from various pipeline stages:
    - Lane reasoning (from lane_reasoning.py)
    - Curvature estimation (from lane_curvature.py)
    - Road type inference (from road_type_inference.py)
    - Lane semantics (from lane_semantics.py)
    """

    def __init__(self):
        pass

    def build(
        self,
        lane_reasoning_result: Dict,
        road_type_result: Dict,
        curvature_result: Dict,
        lane_semantics_result: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> SemanticScene:
        """
        Build complete semantic scene representation.

        Args:
            lane_reasoning_result: Output from LaneReasoner.analyze()
            road_type_result: Output from RoadTypeInference.infer()
            curvature_result: Output from curvature estimation
            lane_semantics_result: Output from lane semantic classification (optional)
            metadata: Additional metadata to include

        Returns:
            SemanticScene object
        """
        scene = SemanticScene()

        # Road information
        scene.road = self._build_road_representation(lane_reasoning_result, road_type_result)

        # Ego lane information
        scene.ego_lane = self._build_ego_lane_representation(lane_reasoning_result)

        # Neighbor lanes
        scene.neighbor_lanes = self._build_neighbor_representation(lane_reasoning_result)

        # Vehicle position
        scene.vehicle_position = self._build_vehicle_position_representation(
            lane_reasoning_result
        )

        # Lane semantics
        if lane_semantics_result:
            scene.lane_semantics = self._build_lane_semantics_representation(
                lane_semantics_result
            )

        # Traffic context
        scene.traffic_context = self._build_traffic_context_representation(
            lane_reasoning_result
        )

        # Metadata
        scene.metadata = metadata or {}
        scene.metadata.update({
            'curvature_confidence': curvature_result.get('confidence', 0),
            'curvature_classification': curvature_result.get('classification', 'unknown')
        })

        return scene

    def _build_road_representation(
        self,
        lane_reasoning: Dict,
        road_type: Dict
    ) -> RoadRepresentation:
        """Build road representation."""
        road_info = road_type.get('road_environment', 'unknown')
        curvature = road_type.get('classification', 'straight')

        # Get lane count
        sorted_lanes = lane_reasoning.get('sorted_lanes', [])
        lane_count = len(sorted_lanes)

        # Estimate road width
        lane_width = lane_reasoning.get('ego_lane', {}).get('lane_width')
        if lane_width:
            width_estimate = lane_width * (lane_count + 1)
        else:
            width_estimate = lane_count * 150  # Rough estimate

        return RoadRepresentation(
            type=road_info,
            curvature=curvature,
            lane_count=lane_count,
            width_estimate=width_estimate,
            convergence="parallel",
            environment=road_info
        )

    def _build_ego_lane_representation(self, lane_reasoning: Dict) -> EgoLaneRepresentation:
        """Build ego lane representation."""
        ego = lane_reasoning.get('ego_lane', {})
        offset = lane_reasoning.get('vehicle_offset', {})

        return EgoLaneRepresentation(
            left_boundary=ego.get('left_boundary_index'),
            right_boundary=ego.get('right_boundary_index'),
            center_x=ego.get('ego_lane_center_x'),
            width_pixels=ego.get('lane_width'),
            offset_ratio=offset.get('offset_ratio_percent', 0) / 100,  # Convert to ratio
            offset_pixels=offset.get('offset_pixels', 0),
            offset_direction=offset.get('direction', 'centered'),
            confidence=ego.get('confidence', 0)
        )

    def _build_neighbor_representation(self, lane_reasoning: Dict) -> NeighborLanesRepresentation:
        """Build neighbor lanes representation."""
        classification = lane_reasoning.get('lane_classification', {})

        return NeighborLanesRepresentation(
            left_count=classification.get('left_neighbor_count', 0),
            right_count=classification.get('right_neighbor_count', 0),
            left_indices=classification.get('left_neighbor_indices', []),
            right_indices=classification.get('right_neighbor_indices', [])
        )

    def _build_vehicle_position_representation(
        self,
        lane_reasoning: Dict
    ) -> VehiclePositionRepresentation:
        """Build vehicle position representation."""
        offset = lane_reasoning.get('vehicle_offset', {})

        return VehiclePositionRepresentation(
            x_pixels=offset.get('vehicle_x', 0),
            lane_center_offset=offset.get('offset_pixels', 0),
            lane_boundary_distances={
                'left': offset.get('distance_to_left_boundary', 0),
                'right': offset.get('distance_to_right_boundary', 0)
            },
            is_centered=offset.get('direction', '') == 'centered',
            is_between_boundaries=offset.get('is_vehicle_between_boundaries', True)
        )

    def _build_lane_semantics_representation(
        self,
        lane_semantics: Dict
    ) -> LaneSemanticsRepresentation:
        """Build lane semantics representation."""
        return LaneSemanticsRepresentation(
            total_lanes=lane_semantics.get('lane_count', 0),
            drivable_lanes=len(lane_semantics.get('drivable_lanes', [])),
            ego_lane_index=lane_semantics.get('ego_lane_index'),
            lane_details=lane_semantics.get('lanes', [])
        )

    def _build_traffic_context_representation(
        self,
        lane_reasoning: Dict
    ) -> TrafficContextRepresentation:
        """Build traffic context representation."""
        road = lane_reasoning.get('road_topology', {})
        neighbor = lane_reasoning.get('lane_classification', {})

        total = neighbor.get('left_neighbor_count', 0) + neighbor.get('right_neighbor_count', 0) + 1

        return TrafficContextRepresentation(
            visible_lanes=road.get('laneline_count', 0),
            lane_direction_type="single_direction",  # For ego-centric reasoning
            confidence="high" if road.get('laneline_count', 0) >= 3 else "medium"
        )


# Convenience function
def build_scene_representation(results: Dict) -> SemanticScene:
    """
    Build scene representation from pipeline results dict.

    Expected dict format:
    {
        'lane_reasoning': {...},
        'road_type': {...},
        'curvature': {...},
        'lane_semantics': {...}  # optional
    }
    """
    builder = SemanticSceneBuilder()
    return builder.build(
        lane_reasoning_result=results.get('lane_reasoning', {}),
        road_type_result=results.get('road_type', {}),
        curvature_result=results.get('curvature', {}),
        lane_semantics_result=results.get('lane_semantics')
    )