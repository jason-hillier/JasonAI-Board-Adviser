from strategic_intelligence_orchestrator import StrategicIntelligenceOrchestrator


def test_orchestrator_exposes_governed_pipeline():
    orchestrator = StrategicIntelligenceOrchestrator()

    assert orchestrator.pipeline == [
        "STRATEGIC_ASSESSMENT",
        "BOARD_SYNTHESIS",
        "PORTFOLIO_INTELLIGENCE",
        "COURSE_CORRECTION",
        "EXECUTIVE_SYNTHESIS",
        "BOARD_BRIEFING",
        "NARRATIVE_ENHANCEMENT",
        "NARRATIVE_GOVERNANCE",
    ]


def test_orchestrator_preserves_governed_transform_position():
    from board_strategic_synthesis import BoardStrategicView
    from board_portfolio_intelligence import synthesise_portfolio
    from strategic_course_correction import (
        StrategicCapabilityGap,
        assess_course_correction,
    )
    from executive_strategic_synthesis import synthesise_executive_strategy

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=["RESOURCE_DEPENDENCY"],
            confidence="HIGH",
            board_implication=(
                "Structural capability constrains strategic delivery."
            ),
            recommended_action=(
                "Address the structural capability constraint."
            ),
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required=(
                "Approve structural capability intervention."
            ),
        ),
    ]

    portfolio = synthesise_portfolio(views)

    capability_gaps = [
        StrategicCapabilityGap(
            capability="Digital origination",
            required_state="Scalable straight-through processing",
            current_state="Manual multi-stage processing",
            gap_type="STRUCTURAL",
            persistence="SUSTAINED",
            materiality="HIGH",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        capability_gaps=capability_gaps,
    )

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
        capability_gaps=capability_gaps,
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(
        executive_view
    )

    assert result.executive_view.strategic_position == "TRANSFORM"
    assert result.executive_view.confidence == "HIGH"
    assert result.executive_view.decision_required == (
        "Approve structural capability intervention."
    )

    assert result.executive_view.traceability.strategic_trigger == (
        "STRATEGIC_CAPABILITY"
    )


def test_orchestrator_generates_board_briefing_from_governed_executive_view():
    from executive_strategic_synthesis import (
        ExecutiveDecisionTraceability,
        ExecutiveStrategicView,
    )

    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary=(
            "The strategic objective remains valid, but current "
            "delivery capability is insufficient."
        ),
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication=(
            "The organisation cannot sustainably deliver the required "
            "strategic outcome using the current capability."
        ),
        recommended_response=(
            "Transform the underlying organisational and technology capability."
        ),
        decision_required="Approve structural capability intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence=(
                "Digital origination remains dependent on manual "
                "multi-stage processing."
            ),
            confidence="HIGH",
        ),
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(executive_view)

    assert result.board_briefing.strategic_position == "TRANSFORM"
    assert result.board_briefing.confidence == "HIGH"
    assert result.board_briefing.decision_required == (
        "Approve structural capability intervention."
    )
    assert result.board_briefing.supporting_evidence == (
        "Digital origination remains dependent on manual multi-stage processing."
    )


def test_orchestrator_result_exposes_enhanced_narrative():
    from dataclasses import fields
    from strategic_intelligence_orchestrator import StrategicIntelligenceResult

    field_names = {
        field.name
        for field in fields(StrategicIntelligenceResult)
    }

    assert "enhanced_narrative" in field_names


def test_orchestrator_populates_enhanced_narrative_without_changing_governed_fields():
    from executive_strategic_synthesis import ExecutiveStrategicView, ExecutiveDecisionTraceability
    from strategic_intelligence_orchestrator import StrategicIntelligenceOrchestrator

    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary="Current capability is insufficient.",
        primary_issue="RESOURCE_DEPENDENCY",
        board_implication="Delivery capability requires structural intervention.",
        recommended_response="Transform the underlying capability.",
        decision_required="Approve structural capability intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence="Manual processing constrains scale.",
            primary_issue="RESOURCE_DEPENDENCY",
            confidence="HIGH",
        ),
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(
        executive_view
    )

    assert result.enhanced_narrative is not None

    assert (
        result.enhanced_narrative.strategic_position
        == result.board_briefing.strategic_position
    )
    assert (
        result.enhanced_narrative.confidence
        == result.board_briefing.confidence
    )
    assert (
        result.enhanced_narrative.decision_required
        == result.board_briefing.decision_required
    )
    assert (
        result.enhanced_narrative.supporting_evidence
        == result.board_briefing.supporting_evidence
    )


def test_strategic_intelligence_result_exposes_strategic_intervention():
    from dataclasses import fields
    from strategic_intelligence_orchestrator import StrategicIntelligenceResult

    field_names = {
        field.name
        for field in fields(StrategicIntelligenceResult)
    }

    assert "strategic_intervention" in field_names


def test_governed_pipeline_populates_strategic_intervention_from_assessment():
    from strategic_intervention import StrategicInterventionAssessment
    from strategic_intelligence_orchestrator import (
        StrategicIntelligenceOrchestrator,
    )

    from executive_strategic_synthesis import (
        ExecutiveDecisionTraceability,
        ExecutiveStrategicView,
    )

    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary=(
            "The strategic objective remains valid, but current "
            "delivery capability is insufficient."
        ),
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication=(
            "The organisation cannot sustainably deliver the required "
            "strategic outcome using the current capability."
        ),
        recommended_response=(
            "Transform the underlying organisational and technology capability."
        ),
        decision_required="Approve structural capability intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence=(
                "Digital origination remains dependent on manual "
                "multi-stage processing."
            ),
            confidence="HIGH",
        ),
    )

    intervention_assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(
        executive_view,
        intervention_assessment=intervention_assessment,
    )

    assert result.strategic_intervention is not None
    assert result.strategic_intervention.primary_intervention == "MODERNISE"
    assert result.strategic_intervention.confidence == "HIGH"


def test_governed_pipeline_does_not_infer_intervention_without_assessment():
    from executive_strategic_synthesis import (
        ExecutiveDecisionTraceability,
        ExecutiveStrategicView,
    )
    from strategic_intelligence_orchestrator import (
        StrategicIntelligenceOrchestrator,
    )

    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary=(
            "The strategic objective remains valid, but current "
            "delivery capability is insufficient."
        ),
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication=(
            "The organisation cannot sustainably deliver the required "
            "strategic outcome using the current capability."
        ),
        recommended_response=(
            "Transform the underlying organisational and technology capability."
        ),
        decision_required="Approve structural capability intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence=(
                "Digital origination remains dependent on manual "
                "multi-stage processing."
            ),
            confidence="HIGH",
        ),
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(
        executive_view
    )

    assert result.strategic_intervention is None


def test_board_briefing_receives_same_governed_strategic_intervention():
    from executive_strategic_synthesis import (
        ExecutiveDecisionTraceability,
        ExecutiveStrategicView,
    )
    from strategic_intervention import StrategicInterventionAssessment
    from strategic_intelligence_orchestrator import (
        StrategicIntelligenceOrchestrator,
    )

    executive_view = ExecutiveStrategicView(
        strategic_position="TRANSFORM",
        executive_summary="Structural capability change is required.",
        primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
        board_implication="Current capability cannot sustain the strategy.",
        recommended_response="Transform the underlying capability.",
        decision_required="Approve structural capability intervention.",
        confidence="HIGH",
        traceability=ExecutiveDecisionTraceability(
            primary_issue="TECHNOLOGY_DELIVERY_CONSTRAINT",
            strategic_trigger="STRATEGIC_CAPABILITY",
            trigger_evidence="Legacy technology constrains delivery.",
            confidence="HIGH",
        ),
    )

    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    orchestrator = StrategicIntelligenceOrchestrator()

    result = orchestrator.run_governed_executive_pipeline(
        executive_view,
        intervention_assessment=assessment,
    )

    assert result.strategic_intervention.primary_intervention == "MODERNISE"

    assert (
        result.board_briefing.strategic_intervention
        is result.strategic_intervention
    )
