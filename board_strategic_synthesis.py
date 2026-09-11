from dataclasses import dataclass, field
from typing import Optional

from strategy_execution_engine import (
    StrategicAssessment,
    OperationalEvidence,
)


@dataclass
class BoardStrategicView:
    trajectory: str
    primary_cause: Optional[str]
    contributing_causes: list[str]
    confidence: str
    board_implication: str
    recommended_action: str
    evidence_rationale: list[str] = field(default_factory=list)


def _humanise_cause(cause: Optional[str]) -> str:
    if not cause:
        return "unresolved strategic factors"

    return cause.replace("_", " ").lower()


def _evidence_supports_cause(
    item: OperationalEvidence,
    cause: Optional[str],
) -> bool:
    """
    Determine whether an evidence item directly supports
    the stated strategic root cause.
    """
    if not cause:
        return False

    metric = item.metric.lower()
    domain = item.domain.lower()

    if cause == "RESOURCE_DEPENDENCY":
        return (
            "single person dependency" in metric
            or "single-person dependency" in metric
            or "key person dependency" in metric
            or "resource availability" in metric
            or "resource dependency" in metric
        )

    if cause == "TECHNOLOGY_DELIVERY_CONSTRAINT":
        return (
            (
                "technology" in domain
                or "technology" in metric
                or "system" in metric
                or "platform" in metric
                or "integration" in metric
            )
            and (
                "defect" in metric
                or "integration" in metric
                or "readiness" in metric
                or "delay" in metric
                or "unresolved" in metric
            )
        )

    if cause == "COMMERCIAL_CONVERSION_WEAKNESS":
        return (
            "conversion" in metric
            or "quote to approval" in metric
            or "approval to payout" in metric
        )

    if cause == "DEMAND_WEAKNESS":
        return (
            "market_demand" in domain
            or "market demand" in domain
            or "qualified opportunity" in metric
            or "pipeline" in metric
        )

    if cause == "PROCESS_CAPACITY_CONSTRAINT":
        approval_signal = (
            "approval" in metric
            and (
                "turnaround" in metric
                or "lead time" in metric
                or "delay" in metric
            )
        )

        broker_signal = (
            "broker" in metric
            and (
                "activation" in metric
                or "onboarding" in metric
                or "lead time" in metric
            )
        )

        return approval_signal or broker_signal

    return False


def _build_evidence_rationale(
    primary_cause: Optional[str],
    evidence: list[OperationalEvidence],
) -> list[str]:
    """
    Create concise, traceable statements describing the evidence
    supporting the primary strategic diagnosis.
    """
    rationale = []

    for item in evidence:
        if not _evidence_supports_cause(
            item,
            primary_cause,
        ):
            continue

        parts = [
            item.metric,
        ]

        if item.variance:
            parts.append(f"variance {item.variance}")

        if item.trend:
            parts.append(f"trend {item.trend.lower()}")

        if item.materiality:
            parts.append(
                f"{item.materiality.lower()} materiality"
            )

        if item.confidence:
            parts.append(
                f"{item.confidence.lower()} confidence"
            )

        if item.source:
            parts.append(f"source: {item.source}")

        rationale.append("; ".join(parts))

    return rationale


def synthesise_for_board(
    assessment: StrategicAssessment,
    evidence: Optional[list[OperationalEvidence]] = None,
) -> BoardStrategicView:
    """
    Convert a detailed strategic assessment into a concise,
    board-level executive view.

    Evidence is optional so existing callers remain compatible.
    When supplied, supporting evidence for the primary cause is
    exposed as an auditable rationale.
    """

    primary_cause = assessment.root_cause

    contributing_causes = list(
        assessment.contributing_causes
    )

    primary_text = _humanise_cause(
        primary_cause
    )

    if primary_cause:
        board_implication = (
            f"Strategic delivery is "
            f"{assessment.trajectory.lower().replace('_', ' ')} "
            f"with {primary_text} identified as the primary constraint."
        )
    else:
        board_implication = (
            f"Strategic delivery is "
            f"{assessment.trajectory.lower().replace('_', ' ')}, "
            "but the primary causal driver has not yet been established."
        )

    if contributing_causes:
        contributing_text = ", ".join(
            _humanise_cause(cause)
            for cause in contributing_causes
        )

        board_implication += (
            f" Contributing factors include "
            f"{contributing_text}."
        )

    recommended_action = (
        assessment.intervention
        if assessment.intervention
        else (
            "Maintain executive oversight and confirm whether "
            "additional corrective action is required."
        )
    )

    evidence_rationale = (
        _build_evidence_rationale(
            primary_cause,
            evidence,
        )
        if evidence
        else []
    )

    return BoardStrategicView(
        trajectory=assessment.trajectory,
        primary_cause=primary_cause,
        contributing_causes=contributing_causes,
        confidence=assessment.confidence,
        board_implication=board_implication,
        recommended_action=recommended_action,
        evidence_rationale=evidence_rationale,
    )
