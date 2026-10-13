from executive_strategic_synthesis import (
    ExecutiveDecisionTraceability,
    ExecutiveStrategicView,
)

from board_briefing_generator import generate_board_briefing


def test_board_briefing_preserves_executive_strategic_position():
    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary=(
            "Strategic position: TRANSFORM. Structural capability "
            "is insufficient to deliver the strategic intent."
        ),
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication=(
            "The strategic objective cannot be delivered sustainably "
            "with the current operating capability."
        ),
        recommended_response=(
            "Transform the underlying organisational capability."
        ),
        decision_required=(
            "Approve structural capability intervention."
        ),
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence=(
                "Digital origination: Manual processing "
                "-> Scalable straight-through processing"
            ),
            confidence="HIGH",
        ),
    )

    briefing = generate_board_briefing(executive_view)

    assert briefing.strategic_position == "TRANSFORM"
    assert briefing.confidence == "HIGH"
    assert briefing.executive_summary
    assert briefing.board_implication
    assert briefing.recommended_response
    assert briefing.decision_required
    assert briefing.supporting_evidence


def test_board_briefing_preserves_governed_decision_and_evidence():
    executive_view = ExecutiveStrategicView(
        strategic_position="RECONSIDER",
        executive_summary=(
            "Strategic position: RECONSIDER. "
            "The strategic thesis has been invalidated."
        ),
        primary_issue="DEMAND_WEAKNESS",
        board_implication=(
            "The basis of the current strategy requires Board review."
        ),
        recommended_response=(
            "Reconsider whether the current strategic direction remains justified."
        ),
        decision_required=(
            "Determine whether the current strategic thesis remains valid."
        ),
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="DEMAND_WEAKNESS",
            strategic_trigger="STRATEGIC_THESIS",
            trigger_evidence=(
                "Persistent structural market contraction."
            ),
            confidence="HIGH",
        ),
    )

    briefing = generate_board_briefing(executive_view)

    assert briefing.strategic_position == executive_view.strategic_position
    assert briefing.confidence == executive_view.confidence
    assert briefing.decision_required == executive_view.decision_required
    assert briefing.supporting_evidence == (
        executive_view.traceability.trigger_evidence
    )


def test_board_briefing_exposes_strategic_intervention():
    from dataclasses import fields
    from board_briefing_generator import BoardBriefing

    field_names = {
        field.name
        for field in fields(BoardBriefing)
    }

    assert "strategic_intervention" in field_names


def test_board_briefing_exposes_board_intervention_summary():
    from dataclasses import fields
    from board_briefing_generator import BoardBriefing

    field_names = {
        field.name
        for field in fields(BoardBriefing)
    }

    assert "intervention_summary" in field_names


def test_board_intervention_summary_has_governed_board_fields():
    from board_briefing_generator import BoardInterventionSummary

    summary = BoardInterventionSummary(
        primary="REDESIGN",
        complementary=["MODERNISE"],
        alternatives=["RECONFIGURE"],
        unsupported=["REINVENT", "REFOUND"],
        confidence="HIGH",
        rationale="The operating model is not fit for the strategic requirement.",
    )

    assert summary.primary == "REDESIGN"
    assert summary.complementary == ["MODERNISE"]
    assert summary.alternatives == ["RECONFIGURE"]
    assert summary.unsupported == ["REINVENT", "REFOUND"]
    assert summary.confidence == "HIGH"
    assert summary.rationale == (
        "The operating model is not fit for the strategic requirement."
    )


def test_build_board_intervention_summary_preserves_governed_intervention():
    from board_briefing_generator import build_board_intervention_summary
    from strategic_intervention import StrategicInterventionResult

    intervention = StrategicInterventionResult(
        primary_intervention="REDESIGN",
        supported_interventions=["REDESIGN", "MODERNISE"],
        complementary_interventions=["MODERNISE"],
        alternative_interventions=["RECONFIGURE"],
        unsupported_interventions=["REINVENT", "REFOUND"],
        rationale="The operating model requires material redesign.",
        confidence="HIGH",
    )

    summary = build_board_intervention_summary(intervention)

    assert summary.primary == "REDESIGN"
    assert summary.complementary == ["MODERNISE"]
    assert summary.alternatives == ["RECONFIGURE"]
    assert summary.unsupported == ["REINVENT", "REFOUND"]
    assert summary.confidence == "HIGH"
    assert summary.rationale == (
        "The operating model requires material redesign."
    )
