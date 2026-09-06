

from strategy_execution_engine import (
    StrategicObjective,
    OperationalEvidence,
    assess_strategy,
)

def test_no_evidence_returns_insufficient_evidence():
    objective = StrategicObjective(
        name="Grow UK originations",
        description="Increase UK equipment finance originations.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    assessment = assess_strategy(objective, {})

    assert assessment.trajectory == "INSUFFICIENT_EVIDENCE"
    assert assessment.confidence == "HIGH"

    
def test_positive_performance_is_on_track():
    objective = StrategicObjective(    name="Grow UK originations",
        description="Increase UK equipment finance originations.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Originations growth",
            actual="18%",
            target="15%",
            variance="+3%",
            period="YTD",
            source="Management Accounts",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "ON_TRACK"

def test_negative_variance_is_at_risk():
    objective = StrategicObjective(
        name="Grow UK originations",
        description="Increase UK equipment finance originations.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Originations growth",
            actual="10%",
            target="15%",
            variance="-5%",
            period="YTD",
            source="Management Accounts",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "AT_RISK"

def test_material_negative_variance_is_off_track():
    objective = StrategicObjective(
        name="Grow UK originations",
        description="Increase UK equipment finance originations.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Originations growth",
            actual="2%",
            target="15%",
            variance="-13%",
            period="YTD",
            source="Management Accounts",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"