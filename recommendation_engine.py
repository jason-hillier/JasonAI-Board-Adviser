from decision_models import DecisionCase, Recommendation
def build_recommendation(case: DecisionCase) -> Recommendation:
    high_risks = [
        risk for risk in case.risks
        if risk.materiality == "HIGH"
    ]

    high_opportunities = [
        opportunity for opportunity in case.opportunities
        if opportunity.materiality == "HIGH"
    ]

    if high_risks and not high_opportunities:
        return Recommendation(
            decision="Do not proceed on the current evidence.",
            rationale="The case contains material high-risk exposure without equivalent high-value opportunity evidence.",
            confidence="MODERATE",
            decision_status="DEFER",
            conditions="Resolve the material risks before reconsideration.",
            evidence_gaps="Further evidence is required to determine whether the risk profile can be improved.",
        )

    return Recommendation(
        decision="Proceed to further evaluation.",
        rationale="The current structured evidence does not justify rejection or unconditional approval.",
        confidence="MODERATE",
        decision_status="PROCEED_WITH_CONDITIONS",
        conditions="Validate material assumptions and outstanding evidence gaps.",
        evidence_gaps="Review unresolved gaps before full commitment.",
    )