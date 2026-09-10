

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

def test_small_negative_variance_is_at_risk():
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
            actual="12%",
            target="15%",
            variance="-3%",
            period="YTD",
            source="Management Accounts",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "AT_RISK"


def test_material_negative_variance_high_priority_is_off_track():
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
    assert assessment.confidence == "HIGH"

def test_material_negative_variance_low_priority_is_at_risk():
    objective = StrategicObjective(
        name="Improve ancillary services",
        description="Increase ancillary service revenue.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="LOW",
    )

    evidence = [
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Ancillary services growth",
            actual="2%",
            target="15%",
            variance="-13%",
            period="YTD",
            source="Management Accounts",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "AT_RISK"

def test_high_priority_negative_variance_deteriorating_is_off_track():
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
            trend="DETERIORATING",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"


def test_high_priority_negative_variance_improving_is_at_risk():
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
            trend="IMPROVING",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "AT_RISK"


def test_mixed_material_trends_deteriorating_overrides_improving():
    objective = StrategicObjective(
        name="Grow UK originations profitably",
        description="Increase originations while protecting profitability.",
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
            trend="IMPROVING",
        ),
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Margin",
            actual="12%",
            target="30%",
            variance="-18%",
            period="YTD",
            source="Management Accounts",
            trend="DETERIORATING",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
