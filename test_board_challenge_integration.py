from executive_strategic_synthesis import (
    ExecutiveDecisionTraceability,
    ExecutiveStrategicView,
)
from strategic_intelligence_orchestrator import (
    StrategicIntelligenceOrchestrator,
)


def make_executive_view():
    return ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary="Current delivery capability is insufficient.",
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication="Structural intervention is required.",
        recommended_response="Modernise the technology platform.",
        decision_required="Approve the proposed intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence="Manual processing constrains delivery.",
            confidence="HIGH",
        ),
    )


def test_challenge_not_requested():
    view = make_executive_view()

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view
    )

    assert result.board_briefing.strategic_challenge is None


def test_challenge_with_complete_inputs():
    view = make_executive_view()

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view,
        challenge_evidence="Approved investment business case.",
        challenge_alternatives=["Replace the platform"],
    )

    challenge = result.board_briefing.strategic_challenge

    assert challenge is not None
    assert challenge.overall_assessment == "NO_GAPS_IDENTIFIED"
    assert len(challenge.findings) == 0
    assert result.executive_view is view
    assert view.recommended_response == "Modernise the technology platform."


def test_challenge_with_missing_evidence_and_alternatives():
    view = make_executive_view()

    result = StrategicIntelligenceOrchestrator().run_governed_executive_pipeline(
        view,
        challenge_evidence="",
        challenge_alternatives=[],
    )

    challenge = result.board_briefing.strategic_challenge

    assert challenge.overall_assessment == "CHALLENGE_REQUIRED"

    categories = {finding.category for finding in challenge.findings}

    assert "EVIDENCE" in categories
    assert "STRATEGIC_ALTERNATIVES" in categories
    assert result.executive_view is view
