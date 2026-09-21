from dataclasses import dataclass

from board_portfolio_intelligence import BoardPortfolioView
from strategic_course_correction import StrategicCourseCorrection


@dataclass
class ExecutiveStrategicView:
    strategic_position: str
    course_of_action: str
    systemic_constraints: list[str]
    priority_issue: str | None
    board_decision: str | None
    rationale: str
    confidence: str


def _board_decision(
    portfolio: BoardPortfolioView,
) -> str | None:
    priority = portfolio.priority_issue

    if (
        priority.primary_cause
        and priority.primary_cause
        in portfolio.material_systemic_constraints
    ):
        intervention = portfolio.strategic_interventions.get(
            priority.primary_cause
        )

        if intervention:
            return intervention.board_action_required

    return priority.decision_required


def synthesise_executive_view(
    portfolio: BoardPortfolioView,
    course_correction: StrategicCourseCorrection,
) -> ExecutiveStrategicView:
    """
    Assemble existing strategic intelligence into a single
    executive-level view.

    This layer does not perform new diagnosis.
    """

    priority = portfolio.priority_issue

    return ExecutiveStrategicView(
        strategic_position=priority.trajectory,
        course_of_action=course_correction.action,
        systemic_constraints=list(
            portfolio.material_systemic_constraints
        ),
        priority_issue=priority.primary_cause,
        board_decision=_board_decision(portfolio),
        rationale=course_correction.rationale,
        confidence=course_correction.confidence,
    )
