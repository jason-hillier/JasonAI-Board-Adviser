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
class StrategicCapabilityGap:
    capability: str
    required_state: str
    current_state: str
    gap_type: str
    persistence: str
    materiality: str
    confidence: str


@dataclass
class StrategicThesis:
    name: str
    thesis: str
    status: str
    evidence: str
    materiality: str
    persistence: str
    confidence: str


@dataclass
class StrategicThesisEvidence:
    thesis: str
    status: str
    evidence: str
    persistence: str
    materiality: str
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


def _transformational_capability_gaps(
    capability_gaps: list[StrategicCapabilityGap],
) -> list[StrategicCapabilityGap]:
    return [
        gap
        for gap in capability_gaps
        if gap.gap_type == "STRUCTURAL"
        and gap.persistence == "SUSTAINED"
        and gap.materiality in {"HIGH", "CRITICAL"}
        and gap.confidence == "HIGH"
    ]


def _invalidated_strategic_theses(
    theses: list[StrategicThesis],
) -> list[StrategicThesis]:
    return [
        thesis
        for thesis in theses
        if thesis.status == "INVALIDATED"
        and thesis.materiality == "CRITICAL"
        and thesis.persistence == "SUSTAINED"
        and thesis.confidence == "HIGH"
    ]


def assess_course_correction(
    portfolio: BoardPortfolioView,
    assumptions: Optional[list[StrategicAssumption]] = None,
    dependencies: Optional[list[StrategicDependency]] = None,
    capability_gaps: Optional[list[StrategicCapabilityGap]] = None,
    theses: Optional[list[StrategicThesis]] = None,
    thesis_evidence: Optional[list[StrategicThesisEvidence]] = None,
) -> StrategicCourseCorrection:
    thesis_evidence = thesis_evidence or []

    invalidated_thesis = [
        item
        for item in thesis_evidence
        if item.status == "INVALIDATED"
        and item.persistence == "SUSTAINED"
        and item.materiality == "CRITICAL"
        and item.confidence == "HIGH"
    ]

    if invalidated_thesis:
        return StrategicCourseCorrection(
            action="RECONSIDER",
            strategy_challenge=True,
            rationale=(
                "High-confidence evidence indicates that the strategic "
                "thesis itself has been invalidated on a sustained and "
                "critical basis. The Board should reconsider whether the "
                "current strategic direction remains justified."
            ),
            confidence="HIGH",
        )

    assumptions = assumptions or []
    dependencies = dependencies or []
    capability_gaps = capability_gaps or []
    theses = theses or []

    invalidated_theses = _invalidated_strategic_theses(
        theses
    )

    if invalidated_theses:
        thesis_names = ", ".join(
            thesis.name
            for thesis in invalidated_theses
        )

        return StrategicCourseCorrection(
            action="RECONSIDER",
            strategy_challenge=True,
            rationale=(
                "Critical, sustained and high-confidence evidence "
                "has invalidated the strategic thesis: "
                f"{thesis_names}. The viability of the current "
                "strategic direction should therefore be reconsidered."
            ),
            confidence="HIGH",
        )

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

    transformational_gaps = _transformational_capability_gaps(
        capability_gaps
    )

    if transformational_gaps:
        capability_names = ", ".join(
            gap.capability
            for gap in transformational_gaps
        )

        return StrategicCourseCorrection(
            action="TRANSFORM",
            strategy_challenge=False,
            rationale=(
                "The strategic direction remains valid, but sustained "
                "structural capability gaps materially constrain the "
                "organisation's ability to deliver it: "
                f"{capability_names}. Transformation of the "
                "underlying capability is required."
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
                "The strategic direction remains valid, but "
                "high-confidence blocking dependencies require the "
                "sequence or timing of strategic objectives to change: "
                f"{dependency_names}."
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
