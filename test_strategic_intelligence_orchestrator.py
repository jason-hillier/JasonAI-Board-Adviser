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

    assert result.strategic_position == "TRANSFORM"
    assert result.confidence == "HIGH"
    assert result.decision_required == (
        "Approve structural capability intervention."
    )

    assert result.traceability.strategic_trigger == (
        "STRATEGIC_CAPABILITY"
    )
