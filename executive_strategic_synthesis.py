from dataclasses import dataclass
from typing import Optional

from board_portfolio_intelligence import BoardPortfolioView
from strategic_course_correction import (
    StrategicAssumption,
    StrategicCapabilityGap,
    StrategicDependency,
    StrategicCourseCorrection,
    StrategicThesisEvidence,
)


@dataclass
class ExecutiveDecisionTraceability:
    primary_issue: Optional[str]
    strategic_trigger: Optional[str]
    trigger_evidence: Optional[str]
    confidence: str


@dataclass
class ExecutiveStrategicView:
    strategic_position: str
    executive_summary: str
    primary_issue: Optional[str]
    board_implication: str
    recommended_response: str
    decision_required: str
    confidence: str
    traceability: ExecutiveDecisionTraceability


def _build_traceability(
    portfolio: BoardPortfolioView,
    course_correction: StrategicCourseCorrection,
    assumptions: list[StrategicAssumption],
    dependencies: list[StrategicDependency],
    capability_gaps: list[StrategicCapabilityGap],
    thesis_evidence: list[StrategicThesisEvidence],
) -> ExecutiveDecisionTraceability:
    strategic_trigger = None
    trigger_evidence = None

    if course_correction.action == "EXECUTE":
        strategic_trigger = "EXECUTION"
        trigger_evidence = portfolio.priority_issue.primary_cause

    elif course_correction.action == "ADAPT":
        qualifying_assumptions = [
            item
            for item in assumptions
            if item.status == "INVALIDATED"
            and item.confidence == "HIGH"
        ]

        if qualifying_assumptions:
            strategic_trigger = "STRATEGIC_ASSUMPTION"
            trigger_evidence = qualifying_assumptions[0].evidence

    elif course_correction.action == "RESEQUENCE":
        qualifying_dependencies = [
            item
            for item in dependencies
            if item.status == "BLOCKING"
            and item.confidence == "HIGH"
        ]

        if qualifying_dependencies:
            dependency = qualifying_dependencies[0]
            strategic_trigger = "STRATEGIC_DEPENDENCY"
            trigger_evidence = (
                f"{dependency.name}: {dependency.prerequisite} "
                f"-> {dependency.dependent_objective}"
            )

    elif course_correction.action == "TRANSFORM":
        qualifying_gaps = [
            item
            for item in capability_gaps
            if item.gap_type == "STRUCTURAL"
            and item.persistence == "SUSTAINED"
            and item.materiality == "HIGH"
            and item.confidence == "HIGH"
        ]

        if qualifying_gaps:
            gap = qualifying_gaps[0]
            strategic_trigger = "STRATEGIC_CAPABILITY"
            trigger_evidence = (
                f"{gap.capability}: {gap.current_state} "
                f"-> {gap.required_state}"
            )

    elif course_correction.action == "RECONSIDER":
        qualifying_evidence = [
            item
            for item in thesis_evidence
            if item.status == "INVALIDATED"
            and item.persistence == "SUSTAINED"
            and item.materiality == "CRITICAL"
            and item.confidence == "HIGH"
        ]

        if qualifying_evidence:
            strategic_trigger = "STRATEGIC_THESIS"
            trigger_evidence = qualifying_evidence[0].evidence

    return ExecutiveDecisionTraceability(
        primary_issue=portfolio.priority_issue.primary_cause,
        strategic_trigger=strategic_trigger,
        trigger_evidence=trigger_evidence,
        confidence=course_correction.confidence,
    )


def synthesise_executive_strategy(
    portfolio: BoardPortfolioView,
    course_correction: StrategicCourseCorrection,
    assumptions: Optional[list[StrategicAssumption]] = None,
    dependencies: Optional[list[StrategicDependency]] = None,
    capability_gaps: Optional[list[StrategicCapabilityGap]] = None,
    thesis_evidence: Optional[list[StrategicThesisEvidence]] = None,
) -> ExecutiveStrategicView:
    """
    Convert portfolio intelligence and strategic course correction
    into a single Board-level strategic recommendation.

    This layer explains existing intelligence. It does not
    independently determine strategic position.
    """

    assumptions = assumptions or []
    dependencies = dependencies or []
    capability_gaps = capability_gaps or []
    thesis_evidence = thesis_evidence or []

    strategic_position = course_correction.action
    priority_issue = portfolio.priority_issue

    executive_summary = (
        f"Strategic position: {strategic_position}. "
        f"{course_correction.rationale}"
    )

    board_implication = priority_issue.board_implication

    if strategic_position == "TRANSFORM":
        recommended_response = (
            "Transform the underlying organisational capability required "
            "to deliver the strategic intent, while protecting the "
            "strategic objective."
        )
    else:
        recommended_response = priority_issue.recommended_action

    decision_required = (
        priority_issue.decision_required
        or "Confirm the proposed strategic response."
    )

    traceability = _build_traceability(
        portfolio,
        course_correction,
        assumptions,
        dependencies,
        capability_gaps,
        thesis_evidence,
    )

    return ExecutiveStrategicView(
        strategic_position=strategic_position,
        executive_summary=executive_summary,
        primary_issue=priority_issue.primary_cause,
        board_implication=board_implication,
        recommended_response=recommended_response,
        decision_required=decision_required,
        confidence=course_correction.confidence,
        traceability=traceability,
    )
