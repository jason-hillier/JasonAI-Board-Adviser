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
    if not evidence:
        return StrategicAssessment(
            objective=objective,
            trajectory="INSUFFICIENT_EVIDENCE",
            diagnosis="No operational evidence has been supplied.",
            strategic_impact="The organisation's current trajectory cannot be assessed reliably.",
            root_cause=None,
            intervention="Provide relevant operational evidence against the strategic objective.",
            confidence="HIGH",
        )

    positive_variances = [
    item for item in evidence
    if item.variance
    and item.variance.strip().startswith("+")
]

    material_negative_variances = []

    for item in evidence:
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

    if material_negative_variances:
        return StrategicAssessment(
            objective=objective,
            trajectory="OFF_TRACK",
            diagnosis=(
                "Operational performance is materially below the stated "
                "strategic target."
            ),
            strategic_impact=(
                "Current performance materially threatens delivery of the "
                "strategic objective."
            ),
            root_cause=None,
            intervention=(
                "Escalate for management intervention, identify the principal "
                "performance drivers, and define corrective actions."
            ),
            confidence="HIGH",
        )

    if positive_variances:
        return StrategicAssessment(
            objective=objective,
            trajectory="ON_TRACK",
            diagnosis="Operational performance is currently ahead of the stated strategic target.",
            strategic_impact="Current performance supports delivery of the strategic objective.",
            root_cause=None,
            intervention=None,
            confidence="MODERATE",
        )

    return StrategicAssessment(
        objective=objective,
        trajectory="AT_RISK",
        diagnosis="Operational evidence does not currently demonstrate performance ahead of target.",
        strategic_impact="The strategic objective may require management intervention to remain achievable.",
        root_cause=None,
        intervention="Review performance drivers and determine whether corrective action is required.",
        confidence="MODERATE",
    )
