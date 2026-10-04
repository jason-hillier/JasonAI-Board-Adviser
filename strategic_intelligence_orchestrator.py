from dataclasses import dataclass

from strategic_intervention import (
    StrategicInterventionAssessment,
    assess_strategic_intervention,
)

from executive_strategic_synthesis import ExecutiveStrategicView
from board_briefing_generator import BoardBriefing, generate_board_briefing
from board_narrative_enhancer import enhance_board_narrative


@dataclass
class StrategicIntelligenceResult:
    executive_view: ExecutiveStrategicView
    board_briefing: BoardBriefing
    enhanced_narrative: object = None
    strategic_intervention: object = None


class StrategicIntelligenceOrchestrator:
    """
    Coordinate the governed strategic intelligence pipeline.

    The orchestrator does not make strategic decisions.
    It delegates intelligence and governance to the
    established specialist layers.
    """

    pipeline = [
        "STRATEGIC_ASSESSMENT",
        "BOARD_SYNTHESIS",
        "PORTFOLIO_INTELLIGENCE",
        "COURSE_CORRECTION",
        "EXECUTIVE_SYNTHESIS",
        "BOARD_BRIEFING",
        "NARRATIVE_ENHANCEMENT",
        "NARRATIVE_GOVERNANCE",
    ]

    def run_governed_executive_pipeline(
        self,
        executive_view: ExecutiveStrategicView,
        intervention_assessment: StrategicInterventionAssessment = None,
    ) -> StrategicIntelligenceResult:
        """
        Pass an already-governed executive strategic view into
        the downstream Board communication pipeline.

        This boundary must not alter strategic position,
        confidence, decision requirements or traceability.
        """

        strategic_intervention = (
            assess_strategic_intervention(intervention_assessment)
            if intervention_assessment is not None
            else None
        )

        board_briefing = generate_board_briefing(executive_view)
        board_briefing.strategic_intervention = strategic_intervention

        enhanced_narrative = enhance_board_narrative(
            board_briefing
        )

        return StrategicIntelligenceResult(
            executive_view=executive_view,
            board_briefing=board_briefing,
            enhanced_narrative=enhanced_narrative,
            strategic_intervention=strategic_intervention,
        )
