from dataclasses import dataclass
from typing import Optional

from strategy_execution_engine import StrategicAssessment


@dataclass
class BoardStrategicView:
    trajectory: str
    primary_cause: Optional[str]
    contributing_causes: list[str]
    confidence: str
    board_implication: str
    recommended_action: str


def _humanise_cause(cause: Optional[str]) -> str:
    if not cause:
        return "unresolved strategic factors"

    return cause.replace("_", " ").lower()


def synthesise_for_board(
    assessment: StrategicAssessment,
) -> BoardStrategicView:
    """
    Convert a detailed strategic assessment into a concise,
    board-level executive view.
    """

    primary_cause = assessment.root_cause
    contributing_causes = list(
        assessment.contributing_causes
    )

    primary_text = _humanise_cause(primary_cause)

    if primary_cause:
        board_implication = (
            f"Strategic delivery is {assessment.trajectory.lower().replace('_', ' ')} "
            f"with {primary_text} identified as the primary constraint."
        )
    else:
        board_implication = (
            f"Strategic delivery is {assessment.trajectory.lower().replace('_', ' ')}, "
            "but the primary causal driver has not yet been established."
        )

    if contributing_causes:
        contributing_text = ", ".join(
            _humanise_cause(cause)
            for cause in contributing_causes
        )

        board_implication += (
            f" Contributing factors include {contributing_text}."
        )

    recommended_action = (
        assessment.intervention
        if assessment.intervention
        else (
            "Maintain executive oversight and confirm whether "
            "additional corrective action is required."
        )
    )

    return BoardStrategicView(
        trajectory=assessment.trajectory,
        primary_cause=primary_cause,
        contributing_causes=contributing_causes,
        confidence=assessment.confidence,
        board_implication=board_implication,
        recommended_action=recommended_action,
    )
