"""
Lane Semantic Understanding

Extensible lane type classification system.

Current lane types:
- dashed: Dashed center line
- solid: Solid lane line
- double_solid: Double solid line
- merge_lane: Merge/egress lane
- exit_lane: Exit ramp lane
- shoulder: Road shoulder
- bike_lane: Bicycle lane
- unknown: Cannot determine

The design supports easy extension for future lane types.
"""


from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from typing_extensions import TypedDict


class LaneType(str, Enum):
    """Lane type enumeration. Extensible."""
    DASHED = "dashed"
    SOLID = "solid"
    DOUBLE_SOLID = "double_solid"
    MERGE_LANE = "merge_lane"
    EXIT_LANE = "exit_lane"
    SHOULDER = "shoulder"
    BIKE_LANE = "bike_lane"
    SIDEWALK = "sidewalk"
    BUS_LANE = "bus_lane"
    HOV_LANE = "hov_lane"
    UNKNOWN = "unknown"


class LaneBoundaryType(str, Enum):
    """Lane boundary type on each side."""
    SOLID = "solid"
    DASHED = "dashed"
    DOUBLE = "double"
    CURB = "curb"
    NONE = "none"
    UNKNOWN = "unknown"


@dataclass
class LaneSemantic:
    """
    Semantic information for a single lane.

    This dataclass is the core semantic representation.
    """
    lane_index: int
    lane_type: LaneType = LaneType.UNKNOWN
    left_boundary: LaneBoundaryType = LaneBoundaryType.UNKNOWN
    right_boundary: LaneBoundaryType = LaneBoundaryType.UNKNOWN
    confidence: float = 0.0
    is_drivable: bool = True
    is_ego_lane: bool = False
    lateral_position: str = "middle"  # "left", "middle", "right", "edge"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "lane_index": self.lane_index,
            "lane_type": self.lane_type.value if isinstance(self.lane_type, Enum) else self.lane_type,
            "left_boundary": self.left_boundary.value if isinstance(self.left_boundary, Enum) else self.left_boundary,
            "right_boundary": self.right_boundary.value if isinstance(self.right_boundary, Enum) else self.right_boundary,
            "confidence": self.confidence,
            "is_drivable": self.is_drivable,
            "is_ego_lane": self.is_ego_lane,
            "lateral_position": self.lateral_position,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'LaneSemantic':
        """Create from dictionary."""
        lane_type = data.get('lane_type', 'unknown')
        if isinstance(lane_type, str):
            try:
                lane_type = LaneType(lane_type)
            except ValueError:
                lane_type = LaneType.UNKNOWN

        left_boundary = data.get('left_boundary', 'unknown')
        if isinstance(left_boundary, str):
            try:
                left_boundary = LaneBoundaryType(left_boundary)
            except ValueError:
                left_boundary = LaneBoundaryType.UNKNOWN

        right_boundary = data.get('right_boundary', 'unknown')
        if isinstance(right_boundary, str):
            try:
                right_boundary = LaneBoundaryType(right_boundary)
            except ValueError:
                right_boundary = LaneBoundaryType.UNKNOWN

        return cls(
            lane_index=data['lane_index'],
            lane_type=lane_type,
            left_boundary=left_boundary,
            right_boundary=right_boundary,
            confidence=data.get('confidence', 0.0),
            is_drivable=data.get('is_drivable', True),
            is_ego_lane=data.get('is_ego_lane', False),
            lateral_position=data.get('lateral_position', 'middle'),
            metadata=data.get('metadata', {})
        )


class LaneSemanticClassifier:
    """
    Classifier for lane types and boundaries.

    This classifier uses geometric heuristics and pattern analysis
    to infer lane semantics. In production, this could be enhanced
    with ML models or road rule databases.
    """

    def __init__(self):
        pass

    def classify(
        self,
        lane_points: List[Tuple[float, float]],
        neighbor_lanes: List[List[Tuple[float, float]]],
        ego_lane_info: Dict,
        lane_index: int,
        image_width: int,
        image_height: int
    ) -> LaneSemantic:
        """
        Classify a single lane's semantics.

        Args:
            lane_points: The lane's point list
            neighbor_lanes: Nearby lanes for context
            ego_lane_info: Ego lane detection results
            lane_index: Index of this lane
            image_width: Image width
            image_height: Image height

        Returns:
            LaneSemantic with classification
        """
        semantic = LaneSemantic(lane_index=lane_index)

        # Determine if this is the ego lane
        if ego_lane_info:
            left_bound = ego_lane_info.get('left_boundary_index')
            right_bound = ego_lane_info.get('right_boundary_index')
            is_left = left_bound is not None and lane_index == left_bound
            is_right = right_bound is not None and lane_index == right_bound
            semantic.is_ego_lane = is_left or is_right

        # Classify boundaries based on lane neighbors
        left_btype, right_btype = self._classify_boundaries(
            lane_index, neighbor_lanes, ego_lane_info, image_width
        )
        semantic.left_boundary = left_btype
        semantic.right_boundary = right_btype

        # Infer lateral position
        semantic.lateral_position = self._infer_lateral_position(
            lane_index, neighbor_lanes, ego_lane_info, image_width
        )

        # Infer drivability
        semantic.is_drivable = self._is_drivable(lane_index, semantic)

        # Set lane type based on context
        semantic.lane_type = self._infer_lane_type(semantic, neighbor_lanes)

        return semantic

    def _classify_boundaries(
        self,
        lane_index: int,
        neighbor_lanes: List[List],
        ego_lane_info: Dict,
        image_width: int
    ) -> Tuple[LaneBoundaryType, LaneBoundaryType]:
        """
        Classify left and right boundaries.

        Heuristics:
        - Center lanes typically have dashed boundaries
        - Edge lanes often have solid outer boundaries
        - Ego lane boundaries depend on traffic rules
        """
        # Default classification based on position relative to ego lane
        # This is a simplified heuristic that can be enhanced

        left_boundary = LaneBoundaryType.DASHED
        right_boundary = LaneBoundaryType.DASHED

        # Check if lane is at image edge (likely solid/curb)
        # Position would be determined from neighbor_lanes

        return left_boundary, right_boundary

    def _infer_lateral_position(
        self,
        lane_index: int,
        neighbor_lanes: List[List],
        ego_lane_info: Dict,
        image_width: int
    ) -> str:
        """Infer lateral position of the lane."""
        if not ego_lane_info:
            return "unknown"

        left_bound = ego_lane_info.get('left_boundary_index')
        right_bound = ego_lane_info.get('right_boundary_index')

        # Determine all lane positions relative to ego
        ego_left = min(left_bound or float('inf'), right_bound or float('inf'))
        ego_right = max(left_bound or -1, right_bound or -1)

        if lane_index < ego_left:
            return "left"
        elif lane_index > ego_right:
            return "right"
        else:
            return "middle"

    def _is_drivable(self, lane_index: int, semantic: LaneSemantic) -> bool:
        """Determine if this lane is drivable."""
        # Shoulders, sidewalks, bike lanes are typically not drivable for vehicles
        non_drivable = {
            LaneType.SHOULDER,
            LaneType.SIDEWALK,
            LaneType.BIKE_LANE,
            LaneType.UNKNOWN
        }

        if semantic.lane_type in non_drivable:
            return False

        return True

    def _infer_lane_type(self, semantic: LaneSemantic, neighbor_lanes: List[List]) -> LaneType:
        """Infer the lane type."""
        # Additional heuristics could be added here
        # For now, use lateral position as basic indicator

        if semantic.lateral_position == "left" or semantic.lateral_position == "right":
            # Edge lanes could be shoulders
            if semantic.lateral_position == "edge":
                return LaneType.SHOULDER

        return LaneType.UNKNOWN  # Default when uncertain


def classify_all_lanes(
    lanes: List[List[Tuple[float, float]]],
    ego_lane_info: Dict,
    image_width: int,
    image_height: int
) -> List[LaneSemantic]:
    """
    Classify semantics for all lanes.

    Args:
        lanes: All lane point lists
        ego_lane_info: Ego lane detection results
        image_width: Image width
        image_height: Image height

    Returns:
        List of LaneSemantic objects
    """
    classifier = LaneSemanticClassifier()
    semantics = []

    for i, lane_points in enumerate(lanes):
        # Get neighbor context
        neighbors = [lanes[j] for j in range(max(0, i-2), min(len(lanes), i+3)) if j != i]

        semantic = classifier.classify(
            lane_points, neighbors, ego_lane_info, i, image_width, image_height
        )
        semantics.append(semantic)

    return semantics


def export_semantics(semantics: List[LaneSemantic]) -> Dict:
    """
    Export lane semantics to structured dictionary.

    Returns LLM-friendly format.
    """
    return {
        "lane_count": len(semantics),
        "lanes": [s.to_dict() for s in semantics],
        "ego_lane_index": next((s.lane_index for s in semantics if s.is_ego_lane), None),
        "drivable_lanes": [s.lane_index for s in semantics if s.is_drivable],
        "non_drivable_lanes": [s.lane_index for s in semantics if not s.is_drivable]
    }