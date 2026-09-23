from dataclasses import replace
from typing import Callable, Optional

from board_briefing_generator import BoardBriefing


NarrativeGenerator = Callable[[BoardBriefing], Optional[dict]]


def enhance_board_narrative(
    briefing: BoardBriefing,
    narrative_generator: Optional[NarrativeGenerator] = None,
) -> BoardBriefing:
    """
    Enhance Board-facing narrative while preserving governed fields.

    Governed fields remain immutable:
    - strategic_position
    - confidence
    - decision_required
    - supporting_evidence

    If narrative enhancement is unavailable or fails, the original
    governed briefing is returned unchanged.
    """

    if narrative_generator is None:
        return briefing

    try:
        narrative = narrative_generator(briefing)
    except Exception:
        return briefing

    if not narrative:
        return briefing

    return replace(
        briefing,
        executive_summary=narrative.get(
            "executive_summary",
            briefing.executive_summary,
        ),
        board_implication=narrative.get(
            "board_implication",
            briefing.board_implication,
        ),
        recommended_response=narrative.get(
            "recommended_response",
            briefing.recommended_response,
        ),
    )
