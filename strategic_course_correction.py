from dataclasses import dataclass
from typing import Optional

from board_portfolio_intelligence import BoardPortfolioView


@dataclass
class StrategicAssumption:
    name: str
    assumption: str
    status: str
    evidence: str
    confidence: str


@dataclass
class StrategicDependency:
    name: str
    prerequisite: str
    dependent_objective: str
    status: str
    confidence: str


@dataclass
class StrategicCourseCorrection:
    action: str
    strategy_challenge: bool
    rationale: str
    confidence: str


def _portfolio_confidence(
    portfolio: BoardPortfolioView,
) -> str:
    if portfolio.strategic_interventions:
        confidence_scores = {
            "LOW": 1,
            "MODERATE": 2,
            "HIGH": 3,
        }

        interventions = list(
            portfolio.strategic_interventions.values()
        )

        return min(
            interventions,
            key=lambda intervention: confidence_scores.get(
                intervention.confidence,
                1,
            ),
        ).confidence

    return portfolio.priority_issue.confidence


def _invalidated_assumptions(
    assumptions: list[StrategicAssumption],
) -> list[StrategicAssumption]:
    return [
        assumption
        for assumption in assumptions
        if assumption.status == "INVALIDATED"
    ]


def _blocking_dependencies(
    dependencies: list[StrategicDependency],
) -> list[StrategicDependency]:
    return [
        dependency
        for dependency in dependencies
        if dependency.status == "BLOCKING"
    ]


def assess_course_correction(
    portfolio: BoardPortfolioView,
    assumptions: Optional[list[StrategicAssumption]] = None,
    dependencies: Optional[list[StrategicDependency]] = None,
) -> StrategicCourseCorrection:
    assumptions = assumptions or []
    dependencies = dependencies or []

    invalidated = _invalidated_assumptions(assumptions)

    high_confidence_invalidated = [
        assumption
        for assumption in invalidated
        if assumption.confidence == "HIGH"
    ]

    if high_confidence_invalidated:
        assumption_names = ", ".join(
            assumption.name
            for assumption in high_confidence_invalidated
        )

        return StrategicCourseCorrection(
            action="ADAPT",
            strategy_challenge=True,
            rationale=(
                "Evidence has invalidated a strategic assumption "
                f"with high confidence: {assumption_names}. "
                "The strategic direction should therefore be adapted "
                "rather than treated solely as an execution problem."
            ),
            confidence="HIGH",
        )

    blocking = _blocking_dependencies(dependencies)

    high_confidence_blocking = [
        dependency
        for dependency in blocking
        if dependency.confidence == "HIGH"
    ]

    if high_confidence_blocking:
        dependency_names = ", ".join(
            dependency.name
            for dependency in high_confidence_blocking
        )

        return StrategicCourseCorrection(
            action="RESEQUENCE",
            strategy_challenge=False,
            rationale=(
                "The strategic direction remains valid, but high-confidence "
                "blocking dependencies require the sequence or timing of "
                f"strategic objectives to change: {dependency_names}."
            ),
            confidence="HIGH",
        )

    return StrategicCourseCorrection(
        action="EXECUTE",
        strategy_challenge=False,
        rationale=(
            "Current evidence identifies execution and delivery "
            "constraints, but does not establish that the underlying "
            "strategic direction is invalid. Correct execution before "
            "changing the strategy."
        ),
        confidence=_portfolio_confidence(portfolio),
    )
