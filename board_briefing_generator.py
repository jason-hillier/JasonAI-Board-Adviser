from dataclasses import dataclass

from executive_strategic_synthesis import ExecutiveStrategicView


@dataclass
class BoardBriefing:
    strategic_position: str
    confidence: str
    executive_summary: str
    board_implication: str
    recommended_response: str
    decision_required: str
    supporting_evidence: str


def generate_board_briefing(
    executive_view: ExecutiveStrategicView,
) -> BoardBriefing:
    """
    Convert the governed Executive Strategic View into a Board briefing.

    This layer communicates established strategic intelligence.
    It does not independently alter strategic position, confidence,
    evidence, or the required Board decision.
    """

    return BoardBriefing(
        strategic_position=executive_view.strategic_position,
        confidence=executive_view.confidence,
        executive_summary=executive_view.executive_summary,
        board_implication=executive_view.board_implication,
        recommended_response=executive_view.recommended_response,
        decision_required=executive_view.decision_required,
        supporting_evidence=(
            executive_view.traceability.trigger_evidence or
            executive_view.traceability.primary_issue or
            "No supporting evidence available."
        ),
    )
