from decision_models import DecisionCase, Risk, EvidenceItem
from recommendation_engine import build_recommendation


def test_high_risk_case_defers():
    case = DecisionCase(
        title="High Risk Test",
        proposal="Test proposal",
        evidence=[
            EvidenceItem(
                statement="Delivery complexity has been independently assessed.",
                evidence_type="FACT",
                materiality="HIGH",
            )
],
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

def test_insufficient_evidence_defers():
    case = DecisionCase(
        title="Insufficient Evidence Test",
        proposal="Invest £10m in a new digital platform",
        evidence=[],
        findings=[],
        risks=[],
        opportunities=[],
        tradeoffs=[],
        options=[],
        recommendation=None,
    )

    recommendation = build_recommendation(case)

    assert recommendation.decision_status == "DEFER"