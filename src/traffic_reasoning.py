"""
Scene Description Generator & LLM Prompt Builder

Generates:
1. Human-readable scene descriptions
2. LLM-ready prompts for traffic reasoning

Design Philosophy:
- Descriptions should be explainable and grounded in observed data
- Prompts should support zero-shot, chain-of-thought, and explainable outputs
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from semantic_scene import SemanticScene


# ============================================================================
# SCENE DESCRIPTION GENERATOR
# ============================================================================


class SceneDescriptionGenerator:
    """
    Generates natural language scene descriptions from semantic scene data.

    The generator produces:
    1. Brief summaries (single sentence)
    2. Full descriptions (multiple sentences)
    3. Technical descriptions (for debugging)
    """

    def __init__(self):
        pass

    def generate_brief(self, scene: SemanticScene) -> str:
        """
        Generate brief one-sentence summary.

        Example: "The vehicle is centered in a multi-lane urban road with one lane on each side."
        """
        parts = []

        # Lane count
        lane_count = scene.road.lane_count
        if lane_count >= 4:
            parts.append(f"a multi-lane road with {lane_count} visible lane boundaries")
        elif lane_count >= 2:
            parts.append("a road with multiple visible lanes")
        else:
            parts.append("a narrow road")

        # Ego lane position
        offset_dir = scene.vehicle_position.lane_center_offset
        if abs(offset_dir) < 10:
            parts.append("The vehicle is centered")
        elif offset_dir < 0:
            parts.append("The vehicle is slightly left of lane center")
        else:
            parts.append("The vehicle is slightly right of lane center")

        # Road curvature
        curvature = scene.road.curvature
        if curvature != 'straight':
            parts.append(f"on a {curvature.replace('_', ' ')}")
        else:
            parts.append("on a straight road")

        return ". ".join(parts) + "."

    def generate_full(self, scene: SemanticScene) -> str:
        """
        Generate detailed multi-sentence description.

        Provides comprehensive scene understanding for human readers.
        """
        sentences = []

        # Sentence 1: Overall scene
        lane_count = scene.road.lane_count
        if lane_count >= 3:
            sentences.append(
                f"The scene shows a multi-lane road with {lane_count} lane boundaries visible in the camera view."
            )
        elif lane_count == 2:
            sentences.append("Two lane boundaries are visible, defining a single driving lane.")
        else:
            sentences.append("A single lane boundary is visible in this scene.")

        # Sentence 2: Ego lane
        left_b = scene.ego_lane.left_boundary
        right_b = scene.ego_lane.right_boundary
        if left_b is not None and right_b is not None:
            sentences.append(
                f"The vehicle is operating within the lane bounded by lane lines {left_b} (left) and {right_b} (right)."
            )

        # Sentence 3: Neighbors
        left_count = scene.neighbor_lanes.left_count
        right_count = scene.neighbor_lanes.right_count

        if left_count == 0 and right_count == 0:
            sentences.append("No neighboring lanes are visible on either side of the ego lane.")
        elif left_count == 0:
            sentences.append(f"There is {right_count} neighboring lane(s) to the right.")
        elif right_count == 0:
            sentences.append(f"There is {left_count} neighboring lane(s) to the left.")
        else:
            sentences.append(
                f"There is {left_count} neighboring lane(s) to the left and {right_count} to the right."
            )

        # Sentence 4: Position
        offset = scene.vehicle_position.lane_center_offset
        if abs(offset) < 10:
            sentences.append("The vehicle is well-centered within its lane.")
        elif offset < 0:
            sentences.append(f"The vehicle is offset {abs(offset):.1f} pixels to the left of lane center.")
        else:
            sentences.append(f"The vehicle is offset {offset:.1f} pixels to the right of lane center.")

        # Sentence 5: Road type
        curvature = scene.road.curvature
        road_type = scene.road.type
        if curvature == 'straight':
            sentences.append("The road ahead appears straight with no significant curves.")
        else:
            curves_desc = curvature.replace('_', ' ')
            sentences.append(f"The road exhibits {curves_desc} characteristics ahead.")

        return " ".join(sentences)

    def generate_technical(self, scene: SemanticScene) -> str:
        """
        Generate technical description for debugging/logging.

        Contains raw values and data.
        """
        lines = [
            "=== SCENE TECHNICAL DESCRIPTION ===",
            f"Scene ID: {scene.scene_id}",
            f"Timestamp: {scene.timestamp}",
            "",
            "Road:",
            f"  Type: {scene.road.type}",
            f"  Curvature: {scene.road.curvature}",
            f"  Lane count: {scene.road.lane_count}",
            f"  Width estimate: {scene.road.width_estimate}",
            "",
            "Ego Lane:",
            f"  Boundaries: {scene.ego_lane.left_boundary} - {scene.ego_lane.right_boundary}",
            f"  Center X: {scene.ego_lane.center_x}",
            f"  Width: {scene.ego_lane.width_pixels}",
            "",
            "Vehicle Position:",
            f"  X: {scene.vehicle_position.x_pixels}",
            f"  Offset: {scene.vehicle_position.lane_center_offset} px",
            f"  Direction: {scene.vehicle_position.lane_boundary_distances}",
            "",
            "Neighboring Lanes:",
            f"  Left: {scene.neighbor_lanes.left_count} lanes",
            f"  Right: {scene.neighbor_lanes.right_count} lanes",
            "",
            "Metadata:",
            f"  Confidence: {scene.metadata.get('curvature_confidence', 'N/A')}",
        ]
        return "\n".join(lines)


# ============================================================================
# LLM PROMPT BUILDER
# ============================================================================


class PromptStrategy(str):
    """Prompt strategy enumeration."""
    ZERO_SHOT = "zero_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    EXPLAINABLE = "explainable"
    SAFETY_FOCUSED = "safety_focused"


@dataclass
class LLMConfiguration:
    """Configuration for LLM prompt generation."""
    model: str = "claude"
    temperature: float = 0.3
    max_tokens: int = 500
    strategy: PromptStrategy = PromptStrategy.ZERO_SHOT


class LLMPromptBuilder:
    """
    Builds LLM prompts from semantic scene representations.

    Supports multiple prompting strategies:
    1. Zero-shot: Direct request for action/classification
    2. Chain-of-thought: Step-by-step reasoning
    3. Explainable: With justification requirements
    4. Safety-focused: Prioritizes safety considerations
    """

    SYSTEM_PROMPTS = {
        PromptStrategy.ZERO_SHOT: """You are a traffic safety assistant analyzing lane and road conditions from sensor data. Provide clear, concise recommendations based on the scene information.""",

        PromptStrategy.CHAIN_OF_THOUGHT: """You are a traffic safety assistant. Analyze the scene step by step:
1. Identify keyroad characteristics
2. Assess vehicle position relative to lane
3. Evaluate potential risks
4. Provide recommendation

Explain your reasoning at each step.""",

        PromptStrategy.EXPLAINABLE: """You are a self-driving system explainer. For each recommendation:
- State the recommendation clearly
- Explain the reasoning using scene evidence
- Note confidence level
- Identify any ambiguities in the data""",

        PromptStrategy.SAFETY_FOCUSED: """You are a conservative driving safety system. Prioritize:
1. Safe following distance
2. Lane keeping
3. Avoiding risky maneuvers
4. Clear signaling

When uncertain, recommend caution.""",
    }

    def __init__(self, config: Optional[LLMConfiguration] = None):
        self.config = config or LLMConfiguration()

    def build_scene_prompt(self, scene: SemanticScene) -> str:
        """
        Build main scene analysis prompt.

        Integrates scene data into natural language format suitable for LLM.
        """
        # Convert scene to text description
        desc = SceneDescriptionGenerator()
        scene_text = desc.generate_brief(scene)

        # Build structured context
        context = self._build_context(scene)

        # Select system prompt based on strategy
        system = self.SYSTEM_PROMPTS.get(self.config.strategy, self.SYSTEM_PROMPTS[PromptStrategy.ZERO_SHOT])

        # Choose user prompt based on strategy
        if self.config.strategy == PromptStrategy.CHAIN_OF_THOUGHT:
            user_prompt = self._build_cot_prompt(scene, context)
        elif self.config.strategy == PromptStrategy.EXPLAINABLE:
            user_prompt = self._build_explainable_prompt(scene, context)
        elif self.config.strategy == PromptStrategy.SAFETY_FOCUSED:
            user_prompt = self._build_safety_prompt(scene, context)
        else:
            user_prompt = self._build_zero_shot_prompt(scene, context)

        return system + "\n\n" + user_prompt

    def _build_context(self, scene: SemanticScene) -> str:
        """Build structured context string from scene."""
        return f"""Road Information:
- Road type: {scene.road.type}
- Curvature: {scene.road.curvature}
- Visible lanes: {scene.road.lane_count}

Ego Lane:
- Position: bounded by lanes {scene.ego_lane.left_boundary} and {scene.ego_lane.right_boundary}
- Width: {scene.ego_lane.width_pixels:.1f} pixels

Vehicle Position:
- Offset from lane center: {scene.vehicle_position.lane_center_offset:.1f} pixels
- Direction: {scene.vehicle_position.lane_boundary_distances.get('left', 'N/A'):.1f}px from left, {scene.vehicle_position.lane_boundary_distances.get('right', 'N/A'):.1f}px from right

Neighboring Lanes:
- Left side: {scene.neighbor_lanes.left_count} lane(s)
- Right side: {scene.neighbor_lanes.right_count} lane(s)"""

    def _build_zero_shot_prompt(self, scene: SemanticScene, context: str) -> str:
        """Build zero-shot prompting prompt."""
        return f"""Analyze this traffic scene and provide your assessment:

{context}

Based on the scene information, provide:
1. A brief situation assessment (1-2 sentences)
2. Any recommended driving actions (be specific)
3. Key safety considerations

Respond concisely."""

    def _build_cot_prompt(self, scene: SemanticScene, context: str) -> str:
        """Build chain-of-thought prompting prompt."""
        return f"""Analyze this traffic scene step by step:

{context}

Think through:
1. What is the current lane configuration? (single/multi-lane, neighbors)
2. How is the vehicle positioned? (centered, left-biased, right-biased)
3. What is the road geometry ahead? (straight, curve direction)
4. Are there immediate risks? (close neighbors, lane departure)
5. What actions, if any, should be considered?

Provide your step-by-step reasoning, then conclude with recommendations."""

    def _build_explainable_prompt(self, scene: SemanticScene, context: str) -> str:
        """Build explainability-focused prompt."""
        return f"""Provide an explainable analysis of this traffic scene:

{context}

For each point, include:
- The observation from the data
- The inference made
- Confidence level

Format as a structured assessment with clear justifications."""

    def _build_safety_prompt(self, scene: SemanticScene, context: str) -> str:
        """Build safety-focused prompt."""
        return f"""Conduct a safety assessment of this driving scene:

{context}

Identify:
1. Immediate safety concerns
2. Safe action recommendations
3. Precautions to consider
4. Any situations requiring extra caution

When recommending lane changes or maneuvers, note the evidence supporting safety."""

    def build_lane_change_prompt(
        self,
        scene: SemanticScene,
        direction: str
    ) -> str:
        """
        Build specialized prompt for lane change reasoning.

        Args:
            scene: Semantic scene representation
            direction: "left" or "right"
        """
        context = self._build_context(scene)
        neighbor_count = (scene.neighbor_lanes.left_count if direction == "left"
                         else scene.neighbor_lanes.right_count)

        return f"""Lane change assessment - request to move {direction}:

{context}

There {'is' if neighbor_count == 1 else 'are'} {neighbor_count} lane(s) to the {direction}.

Assess:
1. Is there sufficient space in the {direction} lane(s)?
2. What is the risk level (low/medium/high)?
3. Is the maneuver recommended?

Consider: lane width, vehicle offset, road curvature."""

    def build_traffic_explanation_prompt(self, scene: SemanticScene) -> str:
        """
        Build prompt for explaining the traffic situation.

        Useful for passenger-facing systems or debugging.
        """
        desc = SceneDescriptionGenerator()
        scene_text = desc.generate_full(scene)

        return f"""Explain this driving scene to a passenger:

{scene_text}

Provide:
1. A simple summary they can understand
2. Points of interest (curves, lane changes visible, etc.)
3. Current driving situation

Use clear, non-technical language."""


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def generate_scene_description(scene: SemanticScene, style: str = "brief") -> str:
    """
    Generate scene description.

    Args:
        scene: Semantic scene representation
        style: "brief", "full", or "technical"
    """
    generator = SceneDescriptionGenerator()

    if style == "brief":
        return generator.generate_brief(scene)
    elif style == "full":
        return generator.generate_full(scene)
    elif style == "technical":
        return generator.generate_technical(scene)
    else:
        return generator.generate_brief(scene)


def build_llm_prompt(
    scene: SemanticScene,
    strategy: PromptStrategy = PromptStrategy.ZERO_SHOT,
    prompt_type: str = "general"
) -> str:
    """
    Build LLM prompt from scene.

    Args:
        scene: Semantic scene representation
        strategy: Prompting strategy
        prompt_type: "general", "lane_change_left", "lane_change_right", or "explanation"
    """
    config = LLMConfiguration(strategy=strategy)
    builder = LLMPromptBuilder(config)

    if prompt_type == "lane_change_left":
        return builder.build_lane_change_prompt(scene, "left")
    elif prompt_type == "lane_change_right":
        return builder.build_lane_change_prompt(scene, "right")
    elif prompt_type == "explanation":
        return builder.build_traffic_explanation_prompt(scene)
    else:
        return builder.build_scene_prompt(scene)