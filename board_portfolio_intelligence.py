from dataclasses import dataclass
from typing import List

from board_strategic_synthesis import BoardStrategicView


@dataclass
class BoardPortfolioView:
    priority_issue: BoardStrategicView


def _priority_score(view: BoardStrategicView) -> tuple[int, int, int]:
    trajectory_scores = {
        "OFF_TRACK": 3,
        "AT_RISK": 2,
        "ON_TRACK": 1,
        "INSUFFICIENT_EVIDENCE": 0,
    }

    escalation_scores = {
        "DECISION": 3,
        "INTERVENTION": 2,
        "ATTENTION": 1,
        "INFORMATION": 0,
    }

    confidence_scores = {
        "HIGH": 3,
        "MODERATE": 2,
        "LOW": 1,
    }

    return (
        trajectory_scores.get(view.trajectory, 0),
        escalation_scores.get(view.escalation_level, 0),
        confidence_scores.get(view.confidence, 0),
    )


def synthesise_portfolio(
    views: List[BoardStrategicView],
) -> BoardPortfolioView:
    priority_issue = max(
        views,
        key=_priority_score,
    )

    return BoardPortfolioView(
        priority_issue=priority_issue,
    )
