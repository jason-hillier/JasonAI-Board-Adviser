

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

def test_low_confidence_evidence_reduces_assessment_confidence():
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
            source="Unverified management estimate",
            trend="DETERIORATING",
            confidence="LOW",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.confidence == "LOW"

def test_multiple_high_confidence_signals_outweigh_single_low_confidence_signal():
    objective = StrategicObjective(
        name="Improve UK business performance",
        description="Deliver sustainable growth and profitability.",
        target="15% improvement",
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
            confidence="HIGH",
        ),
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Margin",
            actual="10%",
            target="25%",
            variance="-15%",
            period="YTD",
            source="Management Accounts",
            trend="DETERIORATING",
            confidence="HIGH",
        ),
        OperationalEvidence(
            domain="OPERATIONAL_PERFORMANCE",
            metric="Processing efficiency",
            actual="70%",
            target="85%",
            variance="-15%",
            period="YTD",
            source="Operational MI",
            trend="DETERIORATING",
            confidence="HIGH",
        ),
        OperationalEvidence(
            domain="MANAGEMENT_SENTIMENT",
            metric="Management outlook",
            actual="Improving",
            target="Positive",
            variance="+5%",
            period="Current",
            source="Management Commentary",
            trend="IMPROVING",
            confidence="LOW",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.confidence == "HIGH"

def test_critical_materiality_deterioration_drives_off_track_assessment():
    objective = StrategicObjective(
        name="Grow UK originations profitably",
        description="Increase originations while maintaining sustainable margin.",
        target="15% profitable growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Net margin",
            actual="12%",
            target="30%",
            variance="-18%",
            period="YTD",
            source="Management Accounts",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        )
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.confidence == "HIGH"

def test_critical_improving_signal_outweighs_low_materiality_deterioration():
    objective = StrategicObjective(
        name="Grow UK originations profitably",
        description="Increase originations while protecting sustainable profitability.",
        target="15% profitable growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="OPERATIONAL_PERFORMANCE",
            metric="Manual processing rate",
            actual="35%",
            target="20%",
            variance="-15%",
            period="YTD",
            source="Operational MI",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="LOW",
        ),
        OperationalEvidence(
            domain="FINANCIAL_PERFORMANCE",
            metric="Net margin",
            actual="18%",
            target="30%",
            variance="-12%",
            period="YTD",
            source="Management Accounts",
            trend="IMPROVING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "AT_RISK"

def test_process_bottleneck_root_cause_and_targeted_intervention():
    objective = StrategicObjective(
        name="Grow UK originations",
        description="Increase UK equipment finance originations.",
        target="15% growth",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="OPERATIONAL_PERFORMANCE",
            metric="Approval turnaround time",
            actual="5 days",
            target="2 days",
            variance="-15%",
            period="YTD",
            source="Operational MI",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
        OperationalEvidence(
            domain="DISTRIBUTION",
            metric="Broker activation lead time",
            actual="8 weeks",
            target="4 weeks",
            variance="-12%",
            period="YTD",
            source="Broker MI",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="HIGH",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.root_cause == "PROCESS_CAPACITY_CONSTRAINT"
    assert "capacity" in assessment.intervention.lower()

def test_resource_dependency_root_cause_and_targeted_intervention():
    objective = StrategicObjective(
        name="Deliver strategic transformation roadmap",
        description="Deliver critical transformation milestones to plan.",
        target="100% critical milestones delivered",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="RESOURCE_CAPACITY",
            metric="Single person dependency",
            actual="Critical dependency exists",
            target="No critical single person dependencies",
            variance="-15%",
            period="Current",
            source="Programme Resource Assessment",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
        OperationalEvidence(
            domain="DELIVERY_PERFORMANCE",
            metric="Milestones delayed by resource availability",
            actual="4 critical milestones delayed",
            target="0 critical milestones delayed",
            variance="-20%",
            period="Current",
            source="Programme MI",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="HIGH",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.root_cause == "RESOURCE_DEPENDENCY"
    assert "resource" in assessment.intervention.lower()

def test_technology_delivery_constraint_root_cause_and_intervention():
    objective = StrategicObjective(
        name="Deliver new asset finance platform",
        description="Implement the strategic technology platform and enable business transition.",
        target="Platform delivered to agreed readiness milestones",
        timeframe="FY27",
        strategic_priority="HIGH",
    )

    evidence = [
        OperationalEvidence(
            domain="TECHNOLOGY_DELIVERY",
            metric="Critical system defects unresolved",
            actual="12 critical defects open",
            target="0 critical defects open",
            variance="-20%",
            period="Current",
            source="Technology Delivery MI",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
        OperationalEvidence(
            domain="TECHNOLOGY_DELIVERY",
            metric="Integration readiness delayed",
            actual="2 critical integrations not ready",
            target="All critical integrations ready",
            variance="-15%",
            period="Current",
            source="Integration Readiness Assessment",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="HIGH",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    assert assessment.trajectory == "OFF_TRACK"
    assert assessment.root_cause == "TECHNOLOGY_DELIVERY_CONSTRAINT"
    assert "technology" in assessment.intervention.lower()
