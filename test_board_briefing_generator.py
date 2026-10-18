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


def test_board_intervention_evidence_traceability_contract():
    from board_briefing_generator import BoardInterventionEvidence

    evidence = BoardInterventionEvidence(
        intervention="REDESIGN",
        dimension="OPERATING_MODEL",
        observed_state="NOT_FIT",
        implication="Operating model change is required.",
        confidence="HIGH",
    )

    assert evidence.intervention == "REDESIGN"
    assert evidence.dimension == "OPERATING_MODEL"
    assert evidence.observed_state == "NOT_FIT"
    assert evidence.implication == "Operating model change is required."
    assert evidence.confidence == "HIGH"


def test_build_redesign_evidence_from_operating_model_assessment():
    from board_briefing_generator import build_board_intervention_evidence
    from strategic_intervention import StrategicInterventionAssessment

    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    evidence = build_board_intervention_evidence(
        assessment,
        intervention="REDESIGN",
    )

    assert evidence.intervention == "REDESIGN"
    assert evidence.dimension == "OPERATING_MODEL"
    assert evidence.observed_state == "NOT_FIT"
    assert evidence.confidence == "HIGH"
    assert "operating model" in evidence.implication.lower()


def test_build_modernise_evidence_from_technology_assessment():
    from board_briefing_generator import build_board_intervention_evidence
    from strategic_intervention import StrategicInterventionAssessment

    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    evidence = build_board_intervention_evidence(
        assessment,
        intervention="MODERNISE",
    )

    assert evidence.intervention == "MODERNISE"
    assert evidence.dimension == "TECHNOLOGY_DATA"
    assert evidence.observed_state == "NOT_FIT"
    assert evidence.confidence == "HIGH"
    assert "technology" in evidence.implication.lower()


def test_build_reconfigure_evidence_from_boundary_assessment():
    from board_briefing_generator import build_board_intervention_evidence
    from strategic_intervention import StrategicInterventionAssessment

    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=False,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    evidence = build_board_intervention_evidence(
        assessment,
        intervention="RECONFIGURE",
    )

    assert evidence.intervention == "RECONFIGURE"
    assert evidence.dimension == "ORGANISATIONAL_BOUNDARIES"
    assert evidence.observed_state == "NOT_FIT"
    assert evidence.confidence == "HIGH"
    assert "boundaries" in evidence.implication.lower()


def test_board_intervention_summary_supports_evidence_records():
    from board_briefing_generator import (
        BoardInterventionSummary,
        BoardInterventionEvidence,
    )

    evidence = BoardInterventionEvidence(
        intervention="REDESIGN",
        dimension="OPERATING_MODEL",
        observed_state="NOT_FIT",
        implication="The operating model requires redesign.",
        confidence="HIGH",
    )

    summary = BoardInterventionSummary(
        primary="REDESIGN",
        complementary=["MODERNISE"],
        alternatives=["RECONFIGURE"],
        unsupported=["REINVENT", "REFOUND"],
        confidence="HIGH",
        rationale="Structural operating model change is required.",
        evidence=[evidence],
    )

    assert len(summary.evidence) == 1
    assert summary.evidence[0].intervention == "REDESIGN"
    assert summary.evidence[0].dimension == "OPERATING_MODEL"


def test_assemble_board_intervention_evidence_for_three_way_scenario():
    from board_briefing_generator import assemble_board_intervention_evidence
    from strategic_intervention import (
        StrategicInterventionAssessment,
        assess_strategic_intervention,
    )

    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=False,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REDESIGN"
    assert result.complementary_interventions == ["MODERNISE"]
    assert result.alternative_interventions == ["RECONFIGURE"]

    evidence = assemble_board_intervention_evidence(
        assessment,
        result,
    )

    assert len(evidence) == 3
    assert [item.intervention for item in evidence] == [
        "REDESIGN",
        "MODERNISE",
        "RECONFIGURE",
    ]
    assert [item.dimension for item in evidence] == [
        "OPERATING_MODEL",
        "TECHNOLOGY_DATA",
        "ORGANISATIONAL_BOUNDARIES",
    ]
    assert all(item.confidence == "HIGH" for item in evidence)
