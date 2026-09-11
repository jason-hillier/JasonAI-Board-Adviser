from dataclasses import dataclass, field
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
    contributing_causes: list[str] = field(default_factory=list)
    root_cause_scores: dict[str, float] = field(default_factory=dict)

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


def _variance_value(
    item: OperationalEvidence,
) -> Optional[float]:
    """Return a numeric percentage variance where available."""
    if not item.variance:
        return None

    variance = item.variance.strip()

    if not variance.endswith("%"):
        return None

    try:
        return float(
            variance.replace("%", "").strip()
        )
    except ValueError:
        return None


def _evidence_strength(
    item: OperationalEvidence,
) -> float:
    """
    Score evidence strength using severity, materiality and confidence.

    Materiality weights are intentionally non-linear so strategically
    critical evidence has appropriate precedence.
    """
    materiality_weights = {
        None: 3,
        "LOW": 1,
        "MODERATE": 3,
        "HIGH": 6,
        "CRITICAL": 10,
    }

    confidence_weights = {
        None: 2,
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
    }

    variance = _variance_value(item)

    if variance is None:
        return 0.0

    severity = abs(variance)

    return (
        severity
        * materiality_weights.get(item.materiality, 3)
        * confidence_weights.get(item.confidence, 2)
    )


def _score_root_causes(
    evidence: list[OperationalEvidence],
) -> dict[str, float]:
    """
    Score candidate strategic root causes using the strongest
    materially negative, deteriorating evidence supporting each cause.
    """

    diagnostic_evidence = []

    for item in evidence:
        variance = _variance_value(item)

        if (
            variance is not None
            and variance <= -10
            and item.trend == "DETERIORATING"
        ):
            diagnostic_evidence.append(item)

    if not diagnostic_evidence:
        return {}

    cause_evidence = {
        "TECHNOLOGY_DELIVERY_CONSTRAINT": [],
        "RESOURCE_DEPENDENCY": [],
        "COMMERCIAL_CONVERSION_WEAKNESS": [],
        "DEMAND_WEAKNESS": [],
        "PROCESS_CAPACITY_CONSTRAINT": [],
    }

    approval_evidence = []
    broker_evidence = []

    for item in diagnostic_evidence:
        metric = item.metric.lower()
        domain = item.domain.lower()

        technology_match = (
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

        if technology_match:
            cause_evidence[
                "TECHNOLOGY_DELIVERY_CONSTRAINT"
            ].append(item)

        resource_match = (
            "single person dependency" in metric
            or "single-person dependency" in metric
            or "key person dependency" in metric
            or "resource availability" in metric
            or "resource dependency" in metric
        )

        if resource_match:
            cause_evidence[
                "RESOURCE_DEPENDENCY"
            ].append(item)

        conversion_match = (
            "conversion" in metric
            or "quote to approval" in metric
            or "approval to payout" in metric
        )

        if conversion_match:
            cause_evidence[
                "COMMERCIAL_CONVERSION_WEAKNESS"
            ].append(item)

        demand_match = (
            "market_demand" in domain
            or "market demand" in domain
            or "qualified opportunity" in metric
            or "pipeline" in metric
        )

        if demand_match:
            cause_evidence[
                "DEMAND_WEAKNESS"
            ].append(item)

        approval_match = (
            "approval" in metric
            and (
                "turnaround" in metric
                or "lead time" in metric
                or "delay" in metric
            )
        )

        broker_match = (
            "broker" in metric
            and (
                "activation" in metric
                or "onboarding" in metric
                or "lead time" in metric
            )
        )

        if approval_match:
            approval_evidence.append(item)

        if broker_match:
            broker_evidence.append(item)

    # A process/capacity diagnosis requires both sides of the pattern.
    if approval_evidence and broker_evidence:
        cause_evidence["PROCESS_CAPACITY_CONSTRAINT"] = (
            approval_evidence + broker_evidence
        )

    scores = {}

    for cause, supporting_evidence in cause_evidence.items():
        if not supporting_evidence:
            continue

        # Use the strongest evidence item for causal precedence.
        # Multiple supporting items strengthen explainability but do not
        # allow quantity alone to overwhelm higher-materiality evidence.
        scores[cause] = max(
            _evidence_strength(item)
            for item in supporting_evidence
        )

    return scores


def _infer_root_cause(
    evidence: list[OperationalEvidence],
) -> Optional[str]:
    """
    Return the highest-ranked strategic root cause.
    """
    scores = _score_root_causes(evidence)

    if not scores:
        return None

    return max(
        scores,
        key=scores.get,
    )


def _infer_contributing_causes(
    evidence: list[OperationalEvidence],
    primary_cause: Optional[str],
) -> list[str]:
    """
    Return secondary causes ranked by evidence strength.
    """
    scores = _score_root_causes(evidence)

    ranked = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [
        cause
        for cause in ranked
        if cause != primary_cause
    ]


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

    if root_cause == "TECHNOLOGY_DELIVERY_CONSTRAINT":
        return (
            "Escalate technology delivery constraints, prioritise critical defects "
            "and integration readiness, confirm recovery ownership, and align "
            "technology capacity to the strategic delivery milestones."
        )

    if root_cause == "COMMERCIAL_CONVERSION_WEAKNESS":
        return (
            "Address conversion weakness across the commercial funnel, identify "
            "drop-off points between quote, approval and payout, review proposition "
            "competitiveness and sales execution, and assign targeted recovery actions."
        )

    if root_cause == "DEMAND_WEAKNESS":
        return (
            "Address the demand shortfall by reviewing market conditions, target "
            "segments, broker and channel activity, proposition competitiveness, "
            "and the volume and quality of opportunities entering the pipeline."
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
                contributing_causes=_infer_contributing_causes(
                    evidence,
                    _infer_root_cause(evidence),
                ),
                root_cause_scores=_score_root_causes(evidence),
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
