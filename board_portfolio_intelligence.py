from dataclasses import dataclass
from collections import Counter

from board_strategic_synthesis import BoardStrategicView


@dataclass
class BoardPortfolioView:
    priority_issue: BoardStrategicView
    systemic_themes: list[str]
    systemic_theme_counts: dict[str, int]
    material_systemic_constraints: list[str]


def _priority_score(
    view: BoardStrategicView,
) -> tuple[int, int, int]:
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


def _causes_for_view(
    view: BoardStrategicView,
) -> set[str]:
    causes = set(view.contributing_causes)

    if view.primary_cause:
        causes.add(view.primary_cause)

    return causes


def _count_causes(
    views: list[BoardStrategicView],
) -> Counter[str]:
    cause_counts: Counter[str] = Counter()

    for view in views:
        cause_counts.update(_causes_for_view(view))

    return cause_counts


def _identify_systemic_themes(
    cause_counts: Counter[str],
) -> list[str]:
    return [
        cause
        for cause, count in cause_counts.items()
        if count >= 2
    ]


def _identify_material_systemic_constraints(
    views: list[BoardStrategicView],
    systemic_themes: list[str],
) -> list[str]:
    material_constraints = []

    for cause in systemic_themes:
        affected_views = [
            view
            for view in views
            if cause in _causes_for_view(view)
        ]

        has_material_escalation = any(
            view.trajectory == "OFF_TRACK"
            and view.escalation_level in {
                "DECISION",
                "INTERVENTION",
            }
            for view in affected_views
        )

        if has_material_escalation:
            material_constraints.append(cause)

    return material_constraints


def synthesise_portfolio(
    views: list[BoardStrategicView],
) -> BoardPortfolioView:
    if not views:
        raise ValueError(
            "At least one BoardStrategicView is required."
        )

    priority_issue = max(
        views,
        key=_priority_score,
    )

    cause_counts = _count_causes(views)
    systemic_themes = _identify_systemic_themes(cause_counts)

    systemic_theme_counts = {
        cause: cause_counts[cause]
        for cause in systemic_themes
    }

    material_systemic_constraints = (
        _identify_material_systemic_constraints(
            views,
            systemic_themes,
        )
    )

    return BoardPortfolioView(
        priority_issue=priority_issue,
        systemic_themes=systemic_themes,
        systemic_theme_counts=systemic_theme_counts,
        material_systemic_constraints=material_systemic_constraints,
    )
