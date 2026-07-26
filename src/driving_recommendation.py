"""
Driving Recommendation System

Tạo prompts cho LLM để đưa ra driving recommendations
dựa trên:
1. Lane geometry + topology
2. Traffic signs
3. Traffic rules
4. Vehicle position
"""

from typing import Dict, List, Optional
from integrated_scene import IntegratedScene


class DrivingRecommendationEngine:
    """
    LLM-powered driving recommendation system.

    Generates structured prompts cho LLM inference:
    - Immediate action recommendations
    - Lane change suggestions
    - Speed adjustments
    - Safety warnings
    """

    # Action priority mapping
    ACTION_PRIORITY = {
        'stop_immediately': 1,
        'prepare_to_stop': 2,
        'yield_to_traffic': 3,
        'slow_down': 4,
        'change_lane_left': 5,
        'change_lane_right': 6,
        'speed_up': 7,
        'maintain_speed': 8,
        'no_action': 99
    }

    def __init__(self):
        pass

    def generate_recommendation(self, scene: IntegratedScene) -> Dict:
        """
        Generate driving recommendation.

        Args:
            scene: IntegratedScene với complete scene info

        Returns:
            Dict với recommendation và reasoning
        """
        recommendation = {
            'action': 'no_action',
            'confidence': 0.5,
            'reasoning': '',
            'immediate_step': '',
            'optional_step': ''
        }

        # Check critical warnings first
        if scene.has_critical_warning:
            recommendation['action'] = 'STOP'
            recommendation['confidence'] = 0.95
            recommendation['immediate_step'] = 'Come to complete stop immediately'

            # Find the warning
            for rule in scene.traffic_rules:
                if rule.get('priority', 99) <= 1:
                    recommendation['reasoning'] = rule.get('description', 'Critical traffic sign detected')
                    recommendation['optional_step'] = 'Check for other traffic before proceeding'
                    break

            return recommendation

        # Check lane change recommendations
        if scene.urgent_action in ['change_lane_left', 'change_lane_right']:
            direction = scene.urgent_action.replace('change_lane_', '')
            recommendation['action'] = 'CHANGE_LANE'
            recommendation['confidence'] = 0.8
            recommendation['immediate_step'] = f'Change lane to {direction}'

            # Check if possible
            if direction == 'left' and scene.neighbor_lanes.get('left_count', 0) > 0:
                recommendation['reasoning'] = 'Lane change needed due to traffic sign'
                recommendation['optional_step'] = 'Check mirrors and blind spot before changing'
            elif direction == 'right' and scene.neighbor_lanes.get('right_count', 0) > 0:
                recommendation['reasoning'] = 'Lane change needed due to traffic sign'
                recommendation['optional_step'] = 'Check mirrors and blind spot before changing'
            else:
                recommendation['action'] = 'PREPARE_STOP'
                recommendation['immediate_step'] = 'No alternate lane available - prepare to stop'
                recommendation['reasoning'] = 'Cannot change lane - no available lane'

            return recommendation

        # Speed-based recommendations
        if scene.recommended_speed is not None:
            if scene.recommended_speed == 0:
                recommendation['action'] = 'STOP'
                recommendation['immediate_step'] = 'Stop the vehicle'
                recommendation['reasoning'] = 'Traffic condition requires stop'
            else:
                recommendation['action'] = 'ADJUST_SPEED'
                recommendation['reasoning'] = f'Speed limit: {scene.recommended_speed} km/h'
                recommendation['optional_step'] = f'Adjust speed to {scene.recommended_speed} km/h'

        # Lane position check
        offset_pixels = scene.vehicle_position.get('offset_pixels', 0)
        if abs(offset_pixels) > 100:  # More than 100px off center
            shift_dir = 'left' if offset_pixels < 0 else 'right'
            recommendation['optional_step'] = f'Consider adjusting position slightly to the {shift_dir}'

        return recommendation

    def build_llm_prompt(self, scene: IntegratedScene) -> str:
        """
        Build LLM prompt từ integrated scene.

        Returns structured prompt for driving recommendation.
        """
        scene_dict = scene.to_dict()

        # Build context
        context = self._build_context(scene_dict)

        # Build recommendation request
        prompt = f"""You are a driving safety assistant. Analyze the following traffic situation and provide recommendations.

{context}

Based on this situation:

1. IMMEDIATE ACTION: What must the driver do RIGHT NOW? (stop, slow down, change lane, continue)
2. REASONING: Why is this action necessary?
3. PRECAUTION: What should the driver be aware of?
4. OPTIONAL: What could improve the driving situation?

Provide a clear, prioritized recommendation. Consider:
- Traffic signs have legal authority - they must be obeyed
- Safety is the top priority
- Lane position and vehicle offset affect stability
- Speed must match road conditions and regulations

FORMAT:
Action: [your recommended action]
Reasoning: [your analysis]
Precautions: [safety considerations]"""

        return prompt

    def build_focused_prompt(
        self,
        scene: IntegratedScene,
        focus: str = 'all'
    ) -> str:
        """
        Build focused prompt cho specific aspects.

        Args:
            focus: 'speed', 'lane', 'signs', 'safety', 'all'
        """
        if focus == 'speed':
            return self._build_speed_focus_prompt(scene)
        elif focus == 'lane':
            return self._build_lane_focus_prompt(scene)
        elif focus == 'signs':
            return self._build_sign_focus_prompt(scene)
        elif focus == 'safety':
            return self._build_safety_focus_prompt(scene)
        else:
            return self.build_llm_prompt(scene)

    def _build_context(self, scene_dict: Dict) -> str:
        """Build context string from scene."""
        road = scene_dict.get('road', {})
        ego = scene_dict.get('ego_lane', {})
        neighbors = scene_dict.get('neighbor_lanes', {})
        vehicle = scene_dict.get('vehicle_position', {})
        signs = scene_dict.get('traffic_signs', {})
        rec = scene_dict.get('driving_recommendation', {})

        context_parts = [
            "=== TRAFFIC SITUATION ===",
            "",
            "ROAD:",
            f"  Type: {road.get('type', 'unknown')}",
            f"  Curvature: {road.get('curvature', 'unknown')}",
            f"  Lanes: {road.get('lane_count', 0)}",
            "",
            "EGO LANE:",
            f"  Between lanes: {ego.get('left_boundary')}-{ego.get('right_boundary')}",
            "",
            "NEIGHBOR LANES:",
            f"  Left: {neighbors.get('left_count', 0)} lane(s)",
            f"  Right: {neighbors.get('right_count', 0)} lane(s)",
            "",
            "VEHICLE POSITION:",
            f"  Offset: {vehicle.get('offset_pixels', 0):.1f} pixels from center",
            f"  Between boundaries: {vehicle.get('between_boundaries', True)}",
            ""
        ]

        # Traffic signs
        if signs.get('count', 0) > 0:
            context_parts.extend([
                "TRAFFIC SIGNS DETECTED:",
                f"  Count: {signs.get('count', 0)}",
                f"  Critical warnings: {'Yes' if signs.get('has_critical', False) else 'No'}",
                f"  Speed limit: {signs.get('active_speed_limit', 'None')} km/h",
                ""
            ])
        else:
            context_parts.extend([
                "TRAFFIC SIGNS:",
                "  None detected",
                ""
            ])

        # Current recommendation
        if rec.get('urgent_action', 'no_action') != 'no_action':
            context_parts.extend([
                "CURRENT RECOMMENDATION:",
                f"  Action: {rec.get('urgent_action', 'none')}",
                f"  Reason: {rec.get('reasoning', 'none')}",
                ""
            ])

        return "\n".join(context_parts)

    def _build_speed_focus_prompt(self, scene: IntegratedScene) -> str:
        """Prompt focused on speed analysis."""
        context = f"""You are analyzing speed requirements for driving.

Current situation:
- Speed limit: {scene.active_speed_limit or 'Not specified'} km/h
- Recommended: {scene.recommended_speed or 'N/A'} km/h
- Road type: {scene.road_info.get('type', 'unknown')}
- Curvature: {scene.road_info.get('curvature', 'unknown')}

Analysis questions:
1. Is the current speed appropriate for conditions?
2. Should speed be reduced ahead of any upcoming sign/situation?
3. Safe following distance considerations?"""
        return context

    def _build_lane_focus_prompt(self, scene: IntegratedScene) -> str:
        """Prompt focused on lane analysis."""
        context = f"""You are analyzing lane selection and positioning.

Current situation:
- Ego lane: {scene.ego_lane.get('left_boundary')}-{scene.ego_lane.get('right_boundary')}
- Vehicle offset: {scene.vehicle_position.get('offset_pixels', 0):.1f} px
- Left neighbors: {scene.neighbor_lanes.get('left_count', 0)}
- Right neighbors: {scene.neighbor_lanes.get('right_count', 0)}

Analysis questions:
1. Is the vehicle well-centered in its lane?
2. Should a lane change be considered?
3. What are the safe lane change options?"""
        return context

    def _build_sign_focus_prompt(self, scene: IntegratedScene) -> str:
        """Prompt focused on traffic signs."""
        sign_str = "\n".join([
            f"  - {s.get('sign_type', 'unknown')} (conf: {s.get('confidence', 0):.0%})"
            for s in scene.detected_signs
        ]) if scene.detected_signs else "  None"

        context = f"""You are analyzing traffic signs and their implications.

Detected signs:
{sign_str}

Priority rules:
"""

        for rule in scene.traffic_rules:
            context += f"\n  [{rule.get('priority', '?')}] {rule.get('description', 'Unknown')}"

        context += """
Analysis questions:
1. Which sign is most critical and why?
2. What is the correct response to each sign?
3. Are there any conflicts between signs?"""
        return context

    def _build_safety_focus_prompt(self, scene: IntegratedScene) -> str:
        """Prompt focused on safety assessment."""
        context = f"""You are performing a safety assessment of the driving situation.

ROAD CONDITIONS:
- Type: {scene.road_info.get('type', 'unknown')}
- Curvature: {scene.road_info.get('curvature', 'unknown')}
- Speed limit: {scene.active_speed_limit or 'Standard'} km/h

VEHICLE POSITION:
- Lane offset: {scene.vehicle_position.get('offset_pixels', 0):.1f} pixels
- Within lane: {'Yes' if scene.vehicle_position.get('between_boundaries', True) else 'No'}

TRAFFIC SIGNS:
- Critical signs: {'Yes' if scene.has_critical_warning else 'No'}
- Active warnings: {len(scene.detected_signs)}

Assessment questions:
1. What are the immediate safety concerns?
2. What defensive driving actions are recommended?
3. What should be watched for in the next 5-10 seconds?"""
        return context


def generate_driving_recommendation(scene: IntegratedScene) -> Dict:
    """
    Quick function to generate driving recommendation.

    Usage:
        scene = create_integrated_scene(lane_reasoning, signs)
        rec = generate_driving_recommendation(scene)
    """
    engine = DrivingRecommendationEngine()
    return engine.generate_recommendation(scene)


def build_driving_prompt(scene: IntegratedScene, focus: str = 'all') -> str:
    """
    Quick function to build LLM prompt.

    Usage:
        prompt = build_driving_prompt(scene, focus='safety')
    """
    engine = DrivingRecommendationEngine()
    return engine.build_focused_prompt(scene, focus=focus)