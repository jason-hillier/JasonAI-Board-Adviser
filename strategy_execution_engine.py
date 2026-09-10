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
@dataclass
class StrategicAssessment:
    objective: StrategicObjective
    trajectory: TrajectoryStatus
    diagnosis: str
    strategic_impact: str
    root_cause: Optional[str] = None
    intervention: Optional[str] = None
    confidence: Literal["LOW", "MODERATE", "HIGH"] = "MODERATE"

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
            confidence="HIGH",
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

        improving_variances = [
            item
            for item in material_negative_variances
            if item.trend == "IMPROVING"
        ]

        deteriorating_variances = [
            item
            for item in material_negative_variances
            if item.trend == "DETERIORATING"
        ]

        # Deteriorating material evidence overrides improving evidence
        # on a high-priority strategic objective.
        if (
            deteriorating_variances
            and objective.strategic_priority == "HIGH"
        ):
            return StrategicAssessment(
                objective=objective,
                trajectory="OFF_TRACK",
                diagnosis=(
                    "Material underperformance includes deteriorating indicators "
                    "on a high-priority strategic objective."
                ),
                strategic_impact=(
                    "The deteriorating evidence materially threatens delivery "
                    "of the strategic objective despite improvement elsewhere."
                ),
                root_cause=None,
                intervention=(
                    "Escalate deteriorating performance drivers, identify the "
                    "underlying causes, and define corrective actions."
                ),
                confidence="HIGH",
            )

        # Materially behind, but all material indicators are demonstrably recovering.
        if improving_variances:
            return StrategicAssessment(
                objective=objective,
                trajectory="AT_RISK",
                diagnosis=(
                    "Operational performance remains materially below target, "
                    "but the direction of travel is improving."
                ),
                strategic_impact=(
                    "The strategic objective remains exposed, but improving "
                    "performance reduces the immediate risk of strategic failure."
                ),
                root_cause=None,
                intervention=(
                    "Continue corrective actions and monitor whether the improving "
                    "trajectory is sufficient to recover the strategic objective."
                ),
                confidence="MODERATE",
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
                confidence="HIGH",
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
            confidence="MODERATE",
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
            confidence="MODERATE",
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
        confidence="MODERATE",
    )
