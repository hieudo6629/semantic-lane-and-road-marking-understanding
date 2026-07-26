"""
Traffic Sign Interpreter

Chuyển đổi detected signs thành semantic traffic rules và actions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from yolo_detector import DetectedSign


class SignCategory(Enum):
    SPEED_LIMIT = "speed_limit"
    REGULATORY = "regulatory"
    TURN_RESTRICTION = "turn_restriction"
    WARNING = "warning"
    TRAFFIC_LIGHT = "traffic_light"
    INFORMATION = "information"


class ActionType(Enum):
    STOP_IMMEDIATELY = "stop_immediately"
    SLOW_DOWN = "slow_down"
    MAINTAIN_SPEED = "maintain_speed"
    SPEED_UP = "speed_up"
    PREPARE_TO_STOP = "prepare_to_stop"
    CHANGE_LANE_LEFT = "change_lane_left"
    CHANGE_LANE_RIGHT = "change_lane_right"
    YIELD_TO_TRAFFIC = "yield_to_traffic"
    NO_ACTION = "no_action"


@dataclass
class TrafficRule:
    category: SignCategory
    description: str
    action_required: ActionType
    priority: int  # Lower = higher priority. STOP=1, WARNING=20, INFO=30+
    speed_limit: Optional[int] = None
    affected_lanes: str = "all"
    reason: str = ""

    def to_dict(self) -> Dict:
        result = {
            'category': self.category.value,
            'description': self.description,
            'action_required': self.action_required.value,
            'priority': self.priority,
            'affected_lanes': self.affected_lanes,
            'reason': self.reason
        }
        if self.speed_limit:
            result['speed_limit'] = self.speed_limit
        return result


@dataclass
class TrafficSituation:
    rules: List[TrafficRule] = field(default_factory=list)
    active_speed_limit: Optional[int] = None
    has_critical_sign: bool = False
    has_warning_sign: bool = False
    urgent_action_required: bool = False
    detected_signs: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'rules': [r.to_dict() for r in self.rules],
            'active_speed_limit': self.active_speed_limit,
            'has_critical_sign': self.has_critical_sign,
            'has_warning_sign': self.has_warning_sign,
            'urgent_action_required': self.urgent_action_required,
            'detected_signs': self.detected_signs
        }


class TrafficSignInterpreter:
    """
    Interpreter: detected signs -> traffic rules.

    Priority scheme (lower = higher priority):
    - 1: STOP (highest)
    - 2: NO ENTRY
    - 3: TRAFFIC LIGHT RED
    - 10: YIELD, TRAFFIC LIGHT YELLOW
    - 20: Speed limits
    - 30: Turn restrictions
    - 40: Warnings
    - 99: Unknown
    """

    DEFAULT_SPEED_LIMIT_URBAN = 50
    DEFAULT_SPEED_LIMIT_HIGHWAY = 80

    PRIORITY_MAP = {
        'stop': 1,
        'no_entry': 2,
        'traffic_light_red': 3,
        'yield': 10,
        'traffic_light_yellow': 10,
        'school_zone': 15,
        'speed_limit_30': 20,
        'speed_limit_50': 20,
        'speed_limit_60': 20,
        'speed_limit_80': 20,
        'speed_limit_100': 20,
        'speed_limit_120': 20,
        'speed_limit_other': 20,
        'no_left_turn': 30,
        'no_right_turn': 30,
        'no_u_turn': 30,
        'pedestrian_crossing': 40,
        'one_way': 50,
        'roundabout': 50,
        'traffic_light_green': 50,
    }

    def __init__(self, is_urban: bool = True):
        self.is_urban = is_urban
        self.default_speed = (self.DEFAULT_SPEED_LIMIT_URBAN if is_urban
                             else self.DEFAULT_SPEED_LIMIT_HIGHWAY)

    def interpret(
        self,
        detected_signs: List[DetectedSign],
        current_speed: Optional[int] = None
    ) -> TrafficSituation:
        situation = TrafficSituation()
        situation.detected_signs = [s.to_dict() for s in detected_signs]

        if not detected_signs:
            return situation

        all_rules = []
        speed_limits = []

        for sign in detected_signs:
            rule = self._interpret_single_sign(sign)
            if rule:
                all_rules.append(rule)
                if rule.speed_limit:
                    speed_limits.append(rule.speed_limit)
                if rule.priority <= 3:
                    situation.has_critical_sign = True
                elif rule.priority <= 15:
                    situation.has_warning_sign = True

        # Sort by priority first, then by distance urgency
        all_rules.sort(key=lambda r: (r.priority, r.reason))

        # Filter conflicting rules (keep lower priority number = more important)
        situation.rules = self._apply_rule_priority(all_rules)

        # Active speed limit
        if speed_limits:
            situation.active_speed_limit = min(speed_limits)
        else:
            situation.active_speed_limit = self.default_speed

        # Urgent check
        situation.urgent_action_required = (
            situation.has_critical_sign or
            self._is_speed_violation(current_speed, situation.active_speed_limit)
        )

        return situation

    def _interpret_single_sign(self, sign: DetectedSign) -> Optional[TrafficRule]:
        sign_type = sign.sign_type
        base_priority = self.PRIORITY_MAP.get(sign_type, 99)

        # Boost priority slightly for very near signs
        near_bonus = 0.5 if sign.distance == "near" else 0.0
        priority = int(base_priority + near_bonus)

        if sign_type.startswith('speed_limit_'):
            speed_value = self._extract_speed(sign_type)
            action = self._action_for_speed(sign.confidence)
            return TrafficRule(
                category=SignCategory.SPEED_LIMIT,
                description=f"Speed limit {speed_value} km/h",
                action_required=action,
                priority=priority,
                speed_limit=speed_value,
                reason=f"Detected {sign_type} ({sign.confidence:.0%}), {sign.distance}"
            )

        if sign_type == 'stop':
            return TrafficRule(
                category=SignCategory.REGULATORY,
                description="STOP - must come to complete stop",
                action_required=ActionType.STOP_IMMEDIATELY,
                priority=priority,
                reason="Stop sign detected"
            )

        if sign_type == 'yield':
            return TrafficRule(
                category=SignCategory.REGULATORY,
                description="YIELD - give way to other traffic",
                action_required=ActionType.YIELD_TO_TRAFFIC,
                priority=priority,
                reason="Yield sign detected"
            )

        if sign_type == 'no_entry':
            return TrafficRule(
                category=SignCategory.REGULATORY,
                description="NO ENTRY - do not proceed",
                action_required=ActionType.STOP_IMMEDIATELY,
                priority=priority,
                reason="No entry sign"
            )

        if sign_type == 'traffic_light_red':
            return TrafficRule(
                category=SignCategory.TRAFFIC_LIGHT,
                description="Red light - must stop",
                action_required=ActionType.STOP_IMMEDIATELY,
                priority=priority,
                reason="Red light"
            )

        if sign_type == 'traffic_light_yellow':
            return TrafficRule(
                category=SignCategory.TRAFFIC_LIGHT,
                description="Yellow light - prepare to stop",
                action_required=ActionType.PREPARE_TO_STOP,
                priority=priority,
                reason="Yellow light"
            )

        if sign_type == 'traffic_light_green':
            return TrafficRule(
                category=SignCategory.TRAFFIC_LIGHT,
                description="Green light - may proceed",
                action_required=ActionType.NO_ACTION,
                priority=priority,
                reason="Green light"
            )

        if sign_type == 'no_left_turn':
            return TrafficRule(
                category=SignCategory.TURN_RESTRICTION,
                description="No left turn",
                action_required=ActionType.CHANGE_LANE_RIGHT,
                priority=priority,
                reason="No left turn sign"
            )

        if sign_type == 'no_right_turn':
            return TrafficRule(
                category=SignCategory.TURN_RESTRICTION,
                description="No right turn",
                action_required=ActionType.CHANGE_LANE_LEFT,
                priority=priority,
                reason="No right turn sign"
            )

        if sign_type == 'no_u_turn':
            return TrafficRule(
                category=SignCategory.TURN_RESTRICTION,
                description="No U-turn",
                action_required=ActionType.NO_ACTION,
                priority=priority,
                reason="No U-turn sign"
            )

        if sign_type == 'pedestrian_crossing':
            return TrafficRule(
                category=SignCategory.WARNING,
                description="Pedestrian crossing - slow down",
                action_required=ActionType.SLOW_DOWN,
                priority=priority,
                reason="Pedestrian crossing"
            )

        if sign_type == 'school_zone':
            return TrafficRule(
                category=SignCategory.WARNING,
                description="School zone - reduced speed",
                action_required=ActionType.SLOW_DOWN,
                priority=priority,
                speed_limit=30,
                reason="School zone"
            )

        return None

    def _extract_speed(self, sign_type: str) -> Optional[int]:
        try:
            speed_str = sign_type.replace('speed_limit_', '')
            return int(speed_str)
        except:
            return None

    def _action_for_speed(self, confidence: float) -> ActionType:
        return ActionType.SPEED_UP if confidence > 0.85 else ActionType.NO_ACTION

    def _apply_rule_priority(self, rules: List[TrafficRule]) -> List[TrafficRule]:
        """Keep only highest-priority rule per category."""
        if not rules:
            return []
        seen = set()
        result = []
        for rule in rules:
            key = (rule.category, rule.action_required)
            if key not in seen:
                result.append(rule)
                seen.add(key)
        return result

    def _is_speed_violation(self, current: Optional[int], limit: int) -> bool:
        return current is not None and current > limit


def interpret_detected_signs(
    signs: List[DetectedSign],
    is_urban: bool = True
) -> TrafficSituation:
    interpreter = TrafficSignInterpreter(is_urban=is_urban)
    return interpreter.interpret(signs)