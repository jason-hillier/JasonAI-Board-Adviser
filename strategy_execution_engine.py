from dataclasses import dataclass
from typing import Literal, Optional


TrajectoryStatus = Literal[
    "ON_TRACK",
    "AT_RISK",
    "OFF_TRACK",
    "INSUFFICIENT_EVIDENCE",
]


@dataclass
class StrategicObjective:
    name: str
    description: str
    target: str
    timeframe: str
    strategic_priority: Literal["LOW", "MEDIUM", "HIGH"]
    owner: Optional[str] = None

@dataclass
class OperationalEvidence:
    domain: Literal[
        "FINANCIAL_PERFORMANCE",
        "CUSTOMERS_AND_MARKETS",
        "COMMERCIAL_OPERATIONS",
        "RISK_AND_COMPLIANCE",
        "PEOPLE_AND_ORGANISATION",
    ]
    metric: str
    actual: str
    target: Optional[str] = None
    variance: Optional[str] = None
    period: Optional[str] = None
    source: Optional[str] = None

    trend: Optional[Literal["IMPROVING", "STABLE", "DETERIORATING"]] = None
    confidence: Optional[Literal["HIGH", "MODERATE", "LOW"]] = None
    materiality: Optional[Literal["CRITICAL", "HIGH", "MODERATE", "LOW"]] = None
@dataclass
class StrategicAssessment:
    objective: StrategicObjective
    trajectory: TrajectoryStatus
    diagnosis: str
    strategic_impact: str
    root_cause: Optional[str] = None
    intervention: Optional[str] = None
    confidence: Literal["LOW", "MODERATE", "HIGH"] = "MODERATE"

def _assessment_confidence(
    evidence: list[OperationalEvidence],
    default: str,
) -> str:
    """
    Aggregate confidence across the available evidence.

    Explicit evidence confidence is scored as:
        LOW = 1
        MODERATE = 2
        HIGH = 3

    The aggregate evidence confidence cannot increase the
    confidence inherent in the strategic assessment rule.
    """
    levels = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
    }

    explicit_scores = [
        levels[item.confidence]
        for item in evidence
        if item.confidence in levels
    ]

    # Preserve legacy/default behaviour where evidence has
    # not been explicitly confidence-rated.
    if not explicit_scores:
        return default

    average_score = sum(explicit_scores) / len(explicit_scores)

    if average_score >= 2.5:
        aggregate = "HIGH"
    elif average_score >= 1.5:
        aggregate = "MODERATE"
    else:
        aggregate = "LOW"

    # Evidence quality may reduce confidence, but it should
    # never inflate the confidence of the underlying rule.
    return (
        aggregate
        if levels[aggregate] < levels[default]
        else default
    )


def _infer_root_cause(
    evidence: list[OperationalEvidence],
) -> Optional[str]:
    """
    Infer a small set of explainable strategic root-cause patterns
    from operational evidence.
    """
    metrics = " ".join(
        item.metric.lower()
        for item in evidence
    )

    approval_constraint = (
        "approval" in metrics
        and (
            "turnaround" in metrics
            or "lead time" in metrics
            or "delay" in metrics
        )
    )

    broker_constraint = (
        "broker" in metrics
        and (
            "activation" in metrics
            or "onboarding" in metrics
            or "lead time" in metrics
        )
    )

    resource_dependency = (
        (
            "single person dependency" in metrics
            or "single-person dependency" in metrics
            or "key person dependency" in metrics
            or "resource availability" in metrics
            or "resource dependency" in metrics
        )
        and (
            "delay" in metrics
            or "milestone" in metrics
            or "dependency" in metrics
            or "availability" in metrics
        )
    )

    if resource_dependency:
        return "RESOURCE_DEPENDENCY"

    if approval_constraint and broker_constraint:
        return "PROCESS_CAPACITY_CONSTRAINT"

    return None


def _root_cause_intervention(
    evidence: list[OperationalEvidence],
) -> str:
    """
    Select an intervention appropriate to the inferred root cause.
    """
    root_cause = _infer_root_cause(evidence)

    if root_cause == "PROCESS_CAPACITY_CONSTRAINT":
        return (
            "Address process and capacity constraints across approval and "
            "broker activation, identify bottlenecks and single-person "
            "dependencies, and rebalance capacity against strategic demand."
        )

    if root_cause == "RESOURCE_DEPENDENCY":
        return (
            "Remove critical resource dependencies by increasing capacity, "
            "cross-training key activities, assigning deputies, and rebalancing "
            "resource demand across competing strategic priorities."
        )

    return (
        "Escalate the highest-materiality deteriorating drivers, "
        "identify root causes, and define corrective actions."
    )


def assess_strategy(
    objective: StrategicObjective,
    evidence: list[OperationalEvidence],
) -> StrategicAssessment:
    """
    Assess whether operational performance supports delivery
    of a strategic objective.
    """

    if not evidence:
        return StrategicAssessment(
            objective=objective,
            trajectory="INSUFFICIENT_EVIDENCE",
            diagnosis="No operational evidence has been supplied.",
            strategic_impact=(
                "The organisation's current trajectory cannot be assessed reliably."
            ),
            root_cause=None,
            intervention=(
                "Provide relevant operational evidence against the strategic objective."
            ),
            confidence=_assessment_confidence(evidence, "HIGH"),
        )

    positive_variances = [
        item
        for item in evidence
        if item.variance
        and item.variance.strip().startswith("+")
    ]

    material_negative_variances = []

    for item in evidence:
        if not item.variance:
            continue

        variance = item.variance.strip()

        if variance.startswith("-") and variance.endswith("%"):
            try:
                variance_value = float(
                    variance.replace("%", "").strip()
                )

                if variance_value <= -10:
                    material_negative_variances.append(item)

            except ValueError:
                pass

    # Material underperformance requires contextual judgement.
    if material_negative_variances:

        materiality_levels = {
            None: 2,
            "LOW": 1,
            "MODERATE": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }

        highest_materiality = max(
            materiality_levels.get(item.materiality, 2)
            for item in material_negative_variances
        )

        decision_variances = [
            item
            for item in material_negative_variances
            if materiality_levels.get(item.materiality, 2)
            == highest_materiality
        ]

        improving_variances = [
            item
            for item in decision_variances
            if item.trend == "IMPROVING"
        ]

        deteriorating_variances = [
            item
            for item in decision_variances
            if item.trend == "DETERIORATING"
        ]

        # Deteriorating evidence at the highest materiality level
        # dominates improving lower-materiality indicators.
        if (
            deteriorating_variances
            and objective.strategic_priority == "HIGH"
        ):
            return StrategicAssessment(
                objective=objective,
                trajectory="OFF_TRACK",
                diagnosis=(
                    "The highest-materiality operational evidence includes "
                    "deteriorating performance on a high-priority objective."
                ),
                strategic_impact=(
                    "The most strategically significant evidence materially "
                    "threatens delivery of the objective."
                ),
                root_cause=_infer_root_cause(evidence),
                intervention=_root_cause_intervention(evidence),
                confidence=_assessment_confidence(evidence, "HIGH"),
            )

        # If the highest-materiality evidence is improving, retain
        # the objective as at risk rather than off track.
        if improving_variances:
            return StrategicAssessment(
                objective=objective,
                trajectory="AT_RISK",
                diagnosis=(
                    "Performance remains materially below target, but the "
                    "highest-materiality evidence is improving."
                ),
                strategic_impact=(
                    "The objective remains exposed, although the most "
                    "strategically significant indicators are recovering."
                ),
                root_cause=None,
                intervention=(
                    "Continue corrective actions and monitor whether recovery "
                    "is sufficient to restore the strategic trajectory."
                ),
                confidence=_assessment_confidence(evidence, "MODERATE"),
            )

        # Material underperformance against a high-priority objective.
        if objective.strategic_priority == "HIGH":
            return StrategicAssessment(
                objective=objective,
                trajectory="OFF_TRACK",
                diagnosis=(
                    "Operational performance is materially below the stated "
                    "strategic target on a high-priority objective."
                ),
                strategic_impact=(
                    "Current performance materially threatens delivery of a "
                    "high-priority strategic objective."
                ),
                root_cause=None,
                intervention=(
                    "Escalate for management intervention, identify the principal "
                    "performance drivers, and define corrective actions."
                ),
                confidence=_assessment_confidence(evidence, "HIGH"),
            )

        # Material variance on a lower-priority objective.
        return StrategicAssessment(
            objective=objective,
            trajectory="AT_RISK",
            diagnosis=(
                "Operational performance is materially below target, but the "
                "objective is not currently classified as high strategic priority."
            ),
            strategic_impact=(
                "The objective requires management attention, but the current "
                "variance does not yet constitute a critical strategic failure."
            ),
            root_cause=None,
            intervention=(
                "Review performance drivers and determine proportionate "
                "corrective action."
            ),
            confidence=_assessment_confidence(evidence, "MODERATE"),
        )

    # Positive performance and no material downside.
    if positive_variances:
        return StrategicAssessment(
            objective=objective,
            trajectory="ON_TRACK",
            diagnosis=(
                "Operational performance is currently ahead of the stated "
                "strategic target."
            ),
            strategic_impact=(
                "Current performance supports delivery of the strategic objective."
            ),
            root_cause=None,
            intervention=None,
            confidence=_assessment_confidence(evidence, "MODERATE"),
        )

    # Default: some evidence exists, but it does not demonstrate
    # either clear outperformance or material strategic failure.
    return StrategicAssessment(
        objective=objective,
        trajectory="AT_RISK",
        diagnosis=(
            "Operational evidence does not currently demonstrate performance "
            "ahead of target."
        ),
        strategic_impact=(
            "The strategic objective may require management intervention "
            "to remain achievable."
        ),
        root_cause=None,
        intervention=(
            "Review performance drivers and determine whether corrective "
            "action is required."
        ),
        confidence=_assessment_confidence(evidence, "MODERATE"),
    )
