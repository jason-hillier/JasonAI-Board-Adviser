from test_board_challenge_integration import make_executive_view
from strategic_intelligence_orchestrator import (
    StrategicIntelligenceOrchestrator,
)


def test_assurance_not_requested():
    view = make_executive_view()

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view
    )

    assert result.board_briefing.strategic_assurance is None


def test_assurance_with_no_evidence():
    view = make_executive_view()

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view,
        assurance_evidence={},
    )

    assurance = result.board_briefing.strategic_assurance

    assert assurance is not None
    assert assurance.overall_status == "MISSING_EVIDENCE"
    assert len(assurance.critical_gaps) == 5
    assert len(assurance.board_questions) == 5


def test_assurance_with_supplied_evidence():
    view = make_executive_view()

    evidence = {
        "STRATEGIC_RATIONALE": ["Approved strategy paper"],
        "INVESTMENT_CASE": ["Financial forecast"],
        "STRATEGIC_ALTERNATIVES": ["Options appraisal"],
        "CRITICAL_ASSUMPTIONS": ["Assumptions register"],
        "DELIVERY_FEASIBILITY": ["Delivery plan"],
    }

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view,
        assurance_evidence=evidence,
    )

    assurance = result.board_briefing.strategic_assurance

    assert assurance.overall_status == "UNVERIFIED"
    assert assurance.critical_gaps == []
    assert all(
        dimension.status == "UNVERIFIED"
        for dimension in assurance.dimensions
    )


def test_assurance_preserves_governed_decision():
    view = make_executive_view()

    original_position = view.strategic_position
    original_confidence = view.confidence
    original_response = view.recommended_response
    original_decision = view.decision_required
    original_traceability = view.traceability

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view,
        assurance_evidence={},
    )

    briefing = result.board_briefing

    assert result.executive_view is view
    assert view.strategic_position == original_position
    assert view.confidence == original_confidence
    assert view.recommended_response == original_response
    assert view.decision_required == original_decision
    assert view.traceability is original_traceability

    assert briefing.strategic_position == original_position
    assert briefing.confidence == original_confidence
    assert briefing.recommended_response == original_response
    assert briefing.decision_required == original_decision
