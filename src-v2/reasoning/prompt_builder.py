"""
Sinh mô tả tự nhiên và prompt cho LLM (Phi-3-mini) từ TrafficScene.

Refactor từ src/traffic_reasoning.py.

THAY ĐỔI QUAN TRỌNG so với bản cũ: `LLMPromptBuilder` cũ chỉ đọc dữ liệu từ
`SemanticScene` (CHỈ có thông tin làn đường) - biển báo/luật giao thông/gợi ý
lái xe (vốn nằm ở integrated_scene.py + driving_recommendation.py) CHƯA BAO
GIỜ được đưa vào bất kỳ prompt LLM nào, dù code cho sign detection đã tồn
tại từ trước. Prompt sinh ra ở đây dùng `analysis.scene_builder.TrafficScene`
(đã gộp cả lane + sign + luật + gợi ý rule-based), nên LLM nhận được đầy đủ
bối cảnh thay vì chỉ một nửa bức tranh.

BUG ĐÃ SỬA: bản cũ có dòng
    f"...{scene.vehicle_position.lane_boundary_distances.get('left', 'N/A'):.1f}..."
Nếu dict không có key 'left' (ví dụ scene chỉ có 1 làn, không xác định được
biên trái), `.get()` trả về chuỗi 'N/A', sau đó áp dụng format spec `:.1f`
lên một CHUỖI sẽ ném `ValueError: Unknown format code 'f' for object of
type 'str'` - crash ngay khi build prompt. Đã sửa bằng hàm format riêng
xử lý None một cách an toàn.

Lưu ý: `PromptStrategy` trong bản cũ kế thừa từ `str` nhưng KHÔNG kế thừa
`Enum` (`class PromptStrategy(str):`) - chạy được nhờ may mắn (các thuộc
tính lớp vẫn là chuỗi thường), nhưng gây hiểu nhầm là Enum thật. Đã sửa
thành `class PromptStrategy(str, Enum)` đúng chuẩn.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

from utils.logger import get_logger

if TYPE_CHECKING:
    from analysis.scene_builder import TrafficScene

logger = get_logger(__name__)


def _fmt(value: Optional[float], suffix: str = "") -> str:
    """Format an toàn cho giá trị số có thể là None - tránh bug format-spec đã mô tả ở đầu file."""
    if value is None:
        return "không xác định"
    return f"{value:.1f}{suffix}"


class SceneDescriber:
    """Sinh mô tả ngôn ngữ tự nhiên (tiếng Anh, vì Phi-3-mini tối ưu cho tiếng Anh) từ TrafficScene."""

    def generate_brief(self, scene: "TrafficScene") -> str:
        """Mô tả ngắn 1-2 câu - dùng cho log/hiển thị nhanh."""
        parts = []
        lane_count = len(scene.lane.sorted_lanes)

        if lane_count >= 4:
            parts.append(f"a multi-lane road with {lane_count} visible lane boundaries")
        elif lane_count >= 2:
            parts.append("a road with multiple visible lanes")
        else:
            parts.append("a narrow road")

        offset = scene.lane.vehicle_offset.offset_pixels
        if abs(offset) < 10:
            parts.append("The vehicle is centered")
        elif offset < 0:
            parts.append("the vehicle is slightly left of lane center")
        else:
            parts.append("the vehicle is slightly right of lane center")

        road_type = scene.road.road_type
        parts.append("on a straight road" if road_type == "straight" else f"on a {road_type.replace('_', ' ')}")

        sentence = ", ".join(parts) + "."

        if scene.traffic_situation.has_critical_sign:
            critical = next((r for r in scene.traffic_situation.rules if r.priority <= 3), None)
            if critical:
                sentence += f" CRITICAL: {critical.description}."

        return sentence

    def generate_full(self, scene: "TrafficScene") -> str:
        """Mô tả đầy đủ nhiều câu, bao gồm cả làn đường lẫn biển báo."""
        sentences = []
        lane_count = len(scene.lane.sorted_lanes)

        if lane_count >= 3:
            sentences.append(f"The scene shows a multi-lane road with {lane_count} lane boundaries visible.")
        elif lane_count == 2:
            sentences.append("Two lane boundaries are visible, defining a single driving lane.")
        else:
            sentences.append("A single lane boundary is visible in this scene.")

        ego = scene.lane.ego_lane
        if ego.left_boundary_index is not None and ego.right_boundary_index is not None:
            sentences.append(
                f"The vehicle is operating within the lane bounded by lane lines "
                f"{ego.left_boundary_index} (left) and {ego.right_boundary_index} (right)."
            )

        left_count = len(scene.lane.left_neighbor_indices)
        right_count = len(scene.lane.right_neighbor_indices)
        if left_count == 0 and right_count == 0:
            sentences.append("No neighboring lanes are visible on either side of the ego lane.")
        else:
            sentences.append(f"There are {left_count} lane(s) to the left and {right_count} to the right.")

        offset = scene.lane.vehicle_offset.offset_pixels
        if abs(offset) < 10:
            sentences.append("The vehicle is well-centered within its lane.")
        else:
            side = "left" if offset < 0 else "right"
            sentences.append(f"The vehicle is offset {abs(offset):.1f} pixels to the {side} of lane center.")

        sentences.append(
            "The road ahead appears straight."
            if scene.road.road_type == "straight"
            else f"The road exhibits {scene.road.road_type.replace('_', ' ')} characteristics ahead."
        )

        if scene.detected_signs:
            sign_list = ", ".join(f"{s.sign_type} ({s.distance})" for s in scene.detected_signs)
            sentences.append(f"Detected traffic signs: {sign_list}.")
            if scene.traffic_situation.active_speed_limit:
                sentences.append(f"Active speed limit: {scene.traffic_situation.active_speed_limit} km/h.")
        else:
            sentences.append("No traffic signs detected in this frame.")

        return " ".join(sentences)

    def generate_technical(self, scene: "TrafficScene") -> str:
        """Mô tả kỹ thuật, chứa số liệu thô - dùng khi debug."""
        lines = [
            "=== SCENE TECHNICAL DESCRIPTION ===",
            f"Scene ID: {scene.scene_id}",
            f"Timestamp: {scene.timestamp}",
            "",
            "Road:",
            f"  Type: {scene.road.road_type}",
            f"  Environment: {scene.road.road_environment}",
            f"  Curvature magnitude: {scene.road.curvature_magnitude:.4f}",
            f"  Lane count: {len(scene.lane.sorted_lanes)}",
            "",
            "Ego Lane:",
            f"  Boundaries: {scene.lane.ego_lane.left_boundary_index} - {scene.lane.ego_lane.right_boundary_index}",
            f"  Center X: {scene.lane.ego_lane.ego_lane_center_x:.1f}",
            f"  Width: {scene.lane.ego_lane.lane_width:.1f}",
            f"  Confidence: {scene.lane.ego_lane.confidence:.2f}",
            "",
            "Vehicle Position:",
            f"  Offset: {scene.lane.vehicle_offset.offset_pixels:.1f} px "
            f"({scene.lane.vehicle_offset.direction})",
            "",
            "Traffic Signs:",
            f"  Count: {len(scene.detected_signs)}",
            f"  Active speed limit: {scene.traffic_situation.active_speed_limit}",
            f"  Critical sign present: {scene.traffic_situation.has_critical_sign}",
            "",
            "Recommendation:",
            f"  Action: {scene.recommendation.action if scene.recommendation else 'N/A'}",
        ]
        return "\n".join(lines)


class PromptStrategy(str, Enum):
    """Chiến lược build prompt cho LLM."""
    ZERO_SHOT = "zero_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    EXPLAINABLE = "explainable"
    SAFETY_FOCUSED = "safety_focused"


@dataclass
class LLMConfig:
    """Cấu hình build prompt. model mặc định là phi-3-mini theo mục tiêu của dự án."""
    model: str = "phi-3-mini"
    temperature: float = 0.3
    max_tokens: int = 500
    strategy: PromptStrategy = PromptStrategy.ZERO_SHOT


# Phi-3-mini là model nhỏ (3.8B), nên giữ system prompt NGẮN GỌN thay vì
# nhiều đoạn văn dài như bản cũ - model nhỏ dễ "lạc hướng" với prompt dài,
# ít bám sát instruction hơn các model lớn.
_SYSTEM_PROMPTS = {
    PromptStrategy.ZERO_SHOT: (
        "You are a traffic safety assistant. Analyze the scene data and give a "
        "clear, concise driving recommendation."
    ),
    PromptStrategy.CHAIN_OF_THOUGHT: (
        "You are a traffic safety assistant. Think step by step: "
        "(1) road/lane state, (2) vehicle position, (3) risks, (4) recommendation. "
        "Explain each step briefly."
    ),
    PromptStrategy.EXPLAINABLE: (
        "You are a self-driving system explainer. For your recommendation, state: "
        "the action, the evidence from the scene data, and your confidence level."
    ),
    PromptStrategy.SAFETY_FOCUSED: (
        "You are a conservative driving safety system. Prioritize lane keeping and "
        "obeying traffic signs. When uncertain, recommend caution."
    ),
}


class PromptBuilder:
    """Build prompt LLM từ TrafficScene - gộp cả bối cảnh làn đường VÀ biển báo."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.describer = SceneDescriber()

    def build_scene_prompt(self, scene: "TrafficScene") -> str:
        """Build prompt chính, chọn system prompt + user prompt theo strategy đã cấu hình."""
        context = self._build_context(scene)
        system = _SYSTEM_PROMPTS.get(self.config.strategy, _SYSTEM_PROMPTS[PromptStrategy.ZERO_SHOT])

        builders = {
            PromptStrategy.CHAIN_OF_THOUGHT: self._build_cot_prompt,
            PromptStrategy.EXPLAINABLE: self._build_explainable_prompt,
            PromptStrategy.SAFETY_FOCUSED: self._build_safety_prompt,
        }
        user_prompt = builders.get(self.config.strategy, self._build_zero_shot_prompt)(context)

        return f"{system}\n\n{user_prompt}"

    def _build_context(self, scene: "TrafficScene") -> str:
        """Build đoạn context súc tích, gộp lane + sign + rule - đây là phần khác biệt lớn nhất so với bản cũ."""
        ego = scene.lane.ego_lane
        offset = scene.lane.vehicle_offset

        lines = [
            "Road:",
            f"- Type: {scene.road.road_type}, environment: {scene.road.road_environment}",
            f"- Visible lanes: {len(scene.lane.sorted_lanes)}",
            "",
            "Ego lane:",
            f"- Bounded by lanes {ego.left_boundary_index} and {ego.right_boundary_index}",
            f"- Width: {_fmt(ego.lane_width, ' px')}",
            f"- Neighbors: {len(scene.lane.left_neighbor_indices)} left, "
            f"{len(scene.lane.right_neighbor_indices)} right",
            "",
            "Vehicle position:",
            f"- Offset from lane center: {_fmt(offset.offset_pixels, ' px')} ({offset.direction})",
            f"- Distance to left/right boundary: {_fmt(offset.distance_to_left_boundary, 'px')} / "
            f"{_fmt(offset.distance_to_right_boundary, 'px')}",
        ]

        if scene.detected_signs:
            lines += ["", "Traffic signs detected:"]
            lines += [
                f"- {s.sign_type} ({s.confidence:.0%} confidence, {s.distance}, {s.relative_position})"
                for s in scene.detected_signs
            ]
            lines += [f"Active speed limit: {scene.traffic_situation.active_speed_limit} km/h"]
        else:
            lines += ["", "Traffic signs: none detected"]

        if scene.recommendation:
            lines += [
                "",
                "Rule-based system recommendation (for reference, you may agree or refine it):",
                f"- Action: {scene.recommendation.action}",
                f"- Reasoning: {scene.recommendation.reasoning}",
            ]

        return "\n".join(lines)

    def _build_zero_shot_prompt(self, context: str) -> str:
        return f"""Analyze this traffic scene and provide your assessment:

{context}

Provide:
1. A brief situation assessment (1-2 sentences)
2. Recommended driving action (be specific)
3. Key safety considerations

Respond concisely."""

    def _build_cot_prompt(self, context: str) -> str:
        return f"""Analyze this traffic scene step by step:

{context}

Think through:
1. Lane configuration (single/multi-lane, neighbors)
2. Vehicle position (centered, left-biased, right-biased)
3. Road geometry ahead (straight, curve direction)
4. Any traffic signs/rules that must be obeyed
5. Immediate risks and recommended action

Provide brief step-by-step reasoning, then conclude with a clear recommendation."""

    def _build_explainable_prompt(self, context: str) -> str:
        return f"""Provide an explainable analysis of this traffic scene:

{context}

For your recommendation, include:
- The observation from the data
- The inference made
- Confidence level (low/medium/high)"""

    def _build_safety_prompt(self, context: str) -> str:
        return f"""Conduct a safety assessment of this driving scene:

{context}

Identify:
1. Immediate safety concerns (especially any traffic signs/rules)
2. Safe action recommendation
3. Precautions for the next few seconds"""

    def build_lane_change_prompt(self, scene: "TrafficScene", direction: str) -> str:
        """Prompt chuyên biệt để đánh giá khả năng đổi làn trái/phải."""
        context = self._build_context(scene)
        neighbor_count = (
            len(scene.lane.left_neighbor_indices) if direction == "left" else len(scene.lane.right_neighbor_indices)
        )

        return f"""Lane change assessment - request to move {direction}:

{context}

There {'is' if neighbor_count == 1 else 'are'} {neighbor_count} lane(s) available to the {direction}.

Assess:
1. Is there sufficient space to change lane {direction}?
2. Risk level (low/medium/high)?
3. Is the maneuver recommended right now?"""


def build_llm_prompt(
    scene: "TrafficScene",
    strategy: PromptStrategy = PromptStrategy.ZERO_SHOT,
    lane_change_direction: Optional[str] = None,
) -> str:
    """Hàm tiện ích: build prompt nhanh mà không cần tự khởi tạo PromptBuilder."""
    builder = PromptBuilder(LLMConfig(strategy=strategy))
    if lane_change_direction in ("left", "right"):
        return builder.build_lane_change_prompt(scene, lane_change_direction)
    return builder.build_scene_prompt(scene)
