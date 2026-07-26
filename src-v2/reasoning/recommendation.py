"""
Diễn giải biển báo thành luật giao thông (traffic rules) và sinh gợi ý lái xe.

Refactor + gộp từ:
- src/traffic_sign_interpreter.py -> SignRuleInterpreter (biển báo -> luật)
- src/driving_recommendation.py   -> RecommendationEngine (scene -> gợi ý hành động)
  (chỉ giữ lại phần generate_recommendation() rule-based; các hàm build_*_prompt()
  của file cũ được CHUYỂN sang reasoning/prompt_builder.py, vì đó là việc build
  chuỗi prompt cho LLM, khác với việc quyết định hành động - gộp chung 2 việc
  vào 1 class như bản cũ khiến docstring cũ ghi nhầm là "LLM-powered" trong khi
  thực chất generate_recommendation() hoàn toàn là rule-based, không gọi LLM).

BUG ĐÃ SỬA: hàm `_action_for_speed()` trong traffic_sign_interpreter.py cũ:

    def _action_for_speed(self, confidence: float) -> ActionType:
        return ActionType.SPEED_UP if confidence > 0.85 else ActionType.NO_ACTION

Hàm này chỉ nhìn vào ĐỘ TỰ TIN của việc NHẬN DIỆN biển báo (confidence của
YOLO), không hề so sánh với TỐC ĐỘ HIỆN TẠI của xe - nghĩa là cứ nhận diện
biển báo tốc độ với độ tự tin > 85% là hệ thống khuyên "TĂNG TỐC", bất kể
biển đó ghi giới hạn bao nhiêu và xe đang chạy bao nhiêu km/h. Đây là lỗi
logic thực sự (không phải chỉ là thiếu tính năng): một biển "tốc độ tối đa
30" vẫn có thể bị diễn giải thành "tăng tốc" nếu YOLO tự tin >85%.

Đã sửa: so sánh current_speed với speed_limit của chính biển báo đó.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from perception.sign_detector import DetectedSign
from utils.logger import get_logger

if TYPE_CHECKING:
    # Chỉ dùng cho type hint - tránh import vòng, vì analysis/scene_builder.py
    # cần import ngược lại SignRuleInterpreter/TrafficSituation từ chính file này.
    from analysis.scene_builder import TrafficScene

logger = get_logger(__name__)


class SignCategory(str, Enum):
    SPEED_LIMIT = "speed_limit"
    REGULATORY = "regulatory"
    TRAFFIC_LIGHT = "traffic_light"
    WARNING = "warning"


class ActionType(str, Enum):
    STOP_IMMEDIATELY = "stop_immediately"
    SLOW_DOWN = "slow_down"
    MAINTAIN_SPEED = "maintain_speed"
    SPEED_UP = "speed_up"
    PREPARE_TO_STOP = "prepare_to_stop"
    YIELD_TO_TRAFFIC = "yield_to_traffic"
    NO_ACTION = "no_action"


@dataclass
class TrafficRule:
    """Một luật giao thông được suy ra từ một biển báo/đèn tín hiệu đã phát hiện."""
    category: SignCategory
    description: str
    action_required: ActionType
    priority: int  # Số càng nhỏ, độ ưu tiên càng cao. STOP=1, cảnh báo=10-15, tốc độ=20
    speed_limit: Optional[int] = None
    reason: str = ""

    def to_dict(self) -> Dict:
        result = {
            "category": self.category.value,
            "description": self.description,
            "action_required": self.action_required.value,
            "priority": self.priority,
            "reason": self.reason,
        }
        if self.speed_limit is not None:
            result["speed_limit"] = self.speed_limit
        return result


@dataclass
class TrafficSituation:
    """Toàn bộ luật giao thông áp dụng cho khung hình hiện tại, đã được rút gọn theo độ ưu tiên."""
    rules: List[TrafficRule] = field(default_factory=list)
    active_speed_limit: Optional[int] = None
    has_critical_sign: bool = False
    has_warning_sign: bool = False
    urgent_action_required: bool = False

    def to_dict(self) -> Dict:
        return {
            "rules": [r.to_dict() for r in self.rules],
            "active_speed_limit": self.active_speed_limit,
            "has_critical_sign": self.has_critical_sign,
            "has_warning_sign": self.has_warning_sign,
            "urgent_action_required": self.urgent_action_required,
        }


class SignRuleInterpreter:
    """Diễn giải danh sách DetectedSign thành TrafficSituation (luật + tốc độ áp dụng)."""

    DEFAULT_SPEED_LIMIT_URBAN = 50
    DEFAULT_SPEED_LIMIT_HIGHWAY = 80

    # Độ ưu tiên: số nhỏ hơn = quan trọng hơn. Xem docstring class TrafficSituation.
    PRIORITY_MAP = {
        "stop": 1,
        "no_entry": 2,
        "traffic_light_red": 3,
        "yield": 10,
        "traffic_light_yellow": 10,
        "school_zone": 15,
        "pedestrian_crossing": 15,
        "traffic_light_green": 50,
    }
    SPEED_LIMIT_PRIORITY = 20

    def __init__(self, is_urban: bool = True):
        self.is_urban = is_urban
        self.default_speed = self.DEFAULT_SPEED_LIMIT_URBAN if is_urban else self.DEFAULT_SPEED_LIMIT_HIGHWAY

    def interpret(
        self,
        detected_signs: List[DetectedSign],
        current_speed: Optional[int] = None,
    ) -> TrafficSituation:
        """
        Args:
            detected_signs: kết quả từ perception.sign_detector.SignDetector.detect().
            current_speed: tốc độ xe hiện tại (km/h), nếu biết - dùng để quyết định
                           tăng/giảm tốc so với biển báo phát hiện được.
        """
        situation = TrafficSituation()
        if not detected_signs:
            situation.active_speed_limit = self.default_speed
            return situation

        rules: List[TrafficRule] = []
        speed_limits: List[int] = []

        for sign in detected_signs:
            rule = self._interpret_single_sign(sign, current_speed)
            if rule is None:
                continue
            rules.append(rule)
            if rule.speed_limit is not None:
                speed_limits.append(rule.speed_limit)
            if rule.priority <= 3:
                situation.has_critical_sign = True
            elif rule.priority <= 15:
                situation.has_warning_sign = True

        rules.sort(key=lambda r: r.priority)
        situation.rules = self._dedupe_by_category_action(rules)
        situation.active_speed_limit = min(speed_limits) if speed_limits else self.default_speed
        situation.urgent_action_required = (
            situation.has_critical_sign or self._is_speed_violation(current_speed, situation.active_speed_limit)
        )
        return situation

    def _interpret_single_sign(self, sign: DetectedSign, current_speed: Optional[int]) -> Optional[TrafficRule]:
        sign_type = sign.sign_type
        near_bonus = 0.5 if sign.distance == "near" else 0.0

        if sign_type.startswith("speed_limit_"):
            speed_value = self._extract_speed(sign_type)
            if speed_value is None:
                return None
            return TrafficRule(
                category=SignCategory.SPEED_LIMIT,
                description=f"Giới hạn tốc độ {speed_value} km/h",
                action_required=self._action_for_speed(speed_value, current_speed),
                priority=int(self.SPEED_LIMIT_PRIORITY + near_bonus),
                speed_limit=speed_value,
                reason=f"Phát hiện biển {sign_type} ({sign.confidence:.0%}), khoảng cách {sign.distance}",
            )

        simple_rules = {
            "stop": ("DỪNG LẠI - phải dừng hẳn xe", ActionType.STOP_IMMEDIATELY, "Phát hiện biển STOP"),
            "yield": ("NHƯỜNG ĐƯỜNG cho xe khác", ActionType.YIELD_TO_TRAFFIC, "Phát hiện biển nhường đường"),
            "no_entry": ("CẤM ĐI VÀO - không được tiếp tục", ActionType.STOP_IMMEDIATELY, "Phát hiện biển cấm vào"),
            "traffic_light_red": ("Đèn đỏ - phải dừng lại", ActionType.STOP_IMMEDIATELY, "Đèn đỏ"),
            "traffic_light_yellow": ("Đèn vàng - chuẩn bị dừng", ActionType.PREPARE_TO_STOP, "Đèn vàng"),
            "traffic_light_green": ("Đèn xanh - được phép đi tiếp", ActionType.NO_ACTION, "Đèn xanh"),
            "pedestrian_crossing": ("Có người đi bộ qua đường - giảm tốc", ActionType.SLOW_DOWN, "Vạch qua đường"),
            "school_zone": ("Khu vực trường học - giảm tốc", ActionType.SLOW_DOWN, "Biển khu vực trường học"),
        }

        if sign_type not in simple_rules:
            return None

        description, action, reason = simple_rules[sign_type]
        speed_limit = 30 if sign_type == "school_zone" else None
        priority = int(self.PRIORITY_MAP.get(sign_type, 99) + near_bonus)

        return TrafficRule(
            category=SignCategory.REGULATORY if sign_type in ("stop", "yield", "no_entry") else (
                SignCategory.TRAFFIC_LIGHT if sign_type.startswith("traffic_light_") else SignCategory.WARNING
            ),
            description=description,
            action_required=action,
            priority=priority,
            speed_limit=speed_limit,
            reason=reason,
        )

    def _extract_speed(self, sign_type: str) -> Optional[int]:
        try:
            return int(sign_type.replace("speed_limit_", ""))
        except ValueError:
            return None

    def _action_for_speed(self, speed_limit: int, current_speed: Optional[int]) -> ActionType:
        """
        Quyết định hành động dựa trên SO SÁNH tốc độ hiện tại với giới hạn của
        biển báo - KHÔNG dựa vào confidence của model detect (xem bug đã sửa
        ở đầu file).
        """
        if current_speed is None:
            return ActionType.NO_ACTION
        if current_speed > speed_limit:
            return ActionType.SLOW_DOWN
        if current_speed < speed_limit * 0.6:
            return ActionType.SPEED_UP
        return ActionType.MAINTAIN_SPEED

    def _dedupe_by_category_action(self, rules: List[TrafficRule]) -> List[TrafficRule]:
        """Giữ luật ưu tiên cao nhất cho mỗi cặp (category, action) - loại luật trùng lặp ý nghĩa."""
        seen = set()
        result = []
        for rule in rules:
            key = (rule.category, rule.action_required)
            if key not in seen:
                seen.add(key)
                result.append(rule)
        return result

    def _is_speed_violation(self, current_speed: Optional[int], limit: int) -> bool:
        return current_speed is not None and current_speed > limit


@dataclass
class Recommendation:
    """Gợi ý hành động lái xe cuối cùng, tổng hợp từ toàn bộ scene (lane + biển báo)."""
    action: str = "no_action"
    confidence: float = 0.5
    reasoning: str = "Tiếp tục di chuyển, chú ý quan sát."
    immediate_step: str = ""
    optional_step: str = ""

    def to_dict(self) -> Dict:
        return {
            "action": self.action,
            "confidence": float(self.confidence),
            "reasoning": self.reasoning,
            "immediate_step": self.immediate_step,
            "optional_step": self.optional_step,
        }


class RecommendationEngine:
    """
    Sinh gợi ý lái xe RULE-BASED (không gọi LLM) từ một TrafficScene hoàn chỉnh.

    Thứ tự ưu tiên xét: biển báo khẩn cấp (STOP/đèn đỏ) > cần đổi làn theo luật
    > điều chỉnh tốc độ > vị trí trong làn.
    """

    def generate(self, scene: "TrafficScene") -> Recommendation:
        situation = scene.traffic_situation

        if situation.has_critical_sign:
            critical_rule = next((r for r in situation.rules if r.priority <= 3), None)
            return Recommendation(
                action="stop",
                confidence=0.95,
                reasoning=critical_rule.description if critical_rule else "Phát hiện biển báo bắt buộc dừng.",
                immediate_step="Dừng xe hoàn toàn ngay lập tức.",
                optional_step="Quan sát xe/người xung quanh trước khi tiếp tục.",
            )

        speed_rec = self._speed_recommendation(scene)
        if speed_rec is not None:
            return speed_rec

        return self._lane_position_recommendation(scene)

    def _speed_recommendation(self, scene: "TrafficScene") -> Optional[Recommendation]:
        situation = scene.traffic_situation
        speed_rule = next((r for r in situation.rules if r.category == SignCategory.SPEED_LIMIT), None)
        if speed_rule is None:
            return None

        if speed_rule.action_required == ActionType.SLOW_DOWN:
            return Recommendation(
                action="slow_down",
                confidence=0.85,
                reasoning=speed_rule.description,
                immediate_step=f"Giảm tốc độ về đúng giới hạn {speed_rule.speed_limit} km/h.",
            )
        if speed_rule.action_required == ActionType.SPEED_UP:
            return Recommendation(
                action="speed_up",
                confidence=0.6,
                reasoning=speed_rule.description,
                optional_step=f"Có thể tăng tốc tới tối đa {speed_rule.speed_limit} km/h nếu điều kiện an toàn.",
            )
        if speed_rule.action_required == ActionType.MAINTAIN_SPEED:
            return Recommendation(
                action="maintain_speed",
                confidence=0.7,
                reasoning=speed_rule.description,
                immediate_step="Giữ nguyên tốc độ hiện tại, đã phù hợp giới hạn.",
            )
        return None

    def _lane_position_recommendation(self, scene: "TrafficScene") -> Recommendation:
        offset = scene.lane.vehicle_offset
        recommendation = Recommendation(
            action="maintain_lane",
            confidence=0.6,
            reasoning="Không có biển báo khẩn cấp, đường và làn hiện tại ổn định.",
            immediate_step="Tiếp tục giữ làn hiện tại.",
        )

        if abs(offset.offset_pixels) > 100:
            shift_dir = "trái" if offset.offset_pixels < 0 else "phải"
            recommendation.optional_step = f"Cân nhắc chỉnh nhẹ vị trí xe sang bên {shift_dir} để căn giữa làn hơn."

        return recommendation


def generate_recommendation(scene: "TrafficScene") -> Recommendation:
    """Hàm tiện ích: tạo RecommendationEngine mặc định và sinh gợi ý ngay."""
    return RecommendationEngine().generate(scene)
