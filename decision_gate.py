from typing import Literal

DecisionClass = Literal[
    "STRUCTURALLY ATTRACTIVE",
    "UNCERTAIN BUT POTENTIALLY ATTRACTIVE",
    "STRUCTURALLY UNATTRACTIVE",
]


def classify_decision_gate(
    market_decline: bool,
    persistent_negative_economics: bool,
    no_competitive_advantage: bool,
    poor_strategic_fit: bool,
    material_opportunity_cost: bool,
) -> DecisionClass:
    """
    Deterministic strategic-thesis gate.

    This does not make the final Board decision.
    It establishes the baseline classification that the
    adjudicator must respect.
    """

    structural_failures = sum(
        [
            market_decline,
            persistent_negative_economics,
            no_competitive_advantage,
            poor_strategic_fit,
            material_opportunity_cost,
        ]
    )

    if structural_failures >= 3:
        return "STRUCTURALLY UNATTRACTIVE"

    if structural_failures == 0:
        return "STRUCTURALLY ATTRACTIVE"

    return "UNCERTAIN BUT POTENTIALLY ATTRACTIVE"