from strategy_execution_engine import (
    StrategicObjective,
    OperationalEvidence,
    assess_strategy,
)

from board_strategic_synthesis import synthesise_for_board


def test_board_synthesis_converts_assessment_into_executive_view():
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
            target="No critical dependencies",
            variance="-30%",
            period="Current",
            source="Programme Resource Assessment",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
        OperationalEvidence(
            domain="TECHNOLOGY_DELIVERY",
            metric="Platform defects unresolved",
            actual="4 defects open",
            target="0 defects open",
            variance="-12%",
            period="Current",
            source="Technology Delivery MI",
            trend="DETERIORATING",
            confidence="MODERATE",
            materiality="HIGH",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    board_view = synthesise_for_board(assessment)

    assert board_view.trajectory == "OFF_TRACK"
    assert board_view.primary_cause == "RESOURCE_DEPENDENCY"
    assert "TECHNOLOGY_DELIVERY_CONSTRAINT" in board_view.contributing_causes
    assert board_view.confidence == assessment.confidence

    assert board_view.board_implication
    assert board_view.recommended_action

    assert "resource" in board_view.board_implication.lower()
    assert "resource" in board_view.recommended_action.lower()

def test_board_synthesis_exposes_evidence_rationale():
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
            target="No critical dependencies",
            variance="-30%",
            period="Current",
            source="Programme Resource Assessment",
            trend="DETERIORATING",
            confidence="HIGH",
            materiality="CRITICAL",
        ),
        OperationalEvidence(
            domain="TECHNOLOGY_DELIVERY",
            metric="Platform defects unresolved",
            actual="4 defects open",
            target="0 defects open",
            variance="-12%",
            period="Current",
            source="Technology Delivery MI",
            trend="DETERIORATING",
            confidence="MODERATE",
            materiality="HIGH",
        ),
    ]

    assessment = assess_strategy(objective, evidence)

    board_view = synthesise_for_board(
        assessment,
        evidence=evidence,
    )

    assert board_view.primary_cause == "RESOURCE_DEPENDENCY"
    assert board_view.evidence_rationale

    rationale = " ".join(board_view.evidence_rationale).lower()

    assert "single person dependency" in rationale
    assert "-30%" in rationale
    assert "critical" in rationale
    assert "high" in rationale
