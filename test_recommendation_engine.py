from decision_models import DecisionCase, Risk
from recommendation_engine import build_recommendation


def test_high_risk_case_defers():
    case = DecisionCase(
        title="High Risk Test",
        proposal="Test proposal",
        evidence=[],
        findings=[],
        risks=[
            Risk(
                title="Material execution risk",
                description="High delivery uncertainty",
                materiality="HIGH",
                likelihood="HIGH",
                impact="HIGH",
            )
        ],
        opportunities=[],
        tradeoffs=[],
        options=[],
        recommendation=None,
    )

    recommendation = build_recommendation(case)

    assert recommendation.decision_status == "DEFER"
    assert recommendation.confidence == "MODERATE"