from board_strategic_synthesis import BoardStrategicView
from board_portfolio_intelligence import synthesise_portfolio
from strategic_course_correction import (
    StrategicCapabilityGap,
    assess_course_correction,
)

from executive_strategic_synthesis import synthesise_executive_strategy


def test_executive_synthesis_converts_transform_into_board_recommendation():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication=(
                "Strategic delivery is constrained by structural "
                "resource and technology capability."
            ),
            recommended_action=(
                "Remove structural delivery constraints."
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
    )

    assert executive_view.strategic_position == "TRANSFORM"
    assert executive_view.confidence == "HIGH"

    assert executive_view.executive_summary
    assert executive_view.board_implication
    assert executive_view.recommended_response
    assert executive_view.decision_required

    assert "transform" in executive_view.executive_summary.lower()
    assert "capability" in executive_view.recommended_response.lower()

    assert executive_view.primary_issue == portfolio.priority_issue.primary_cause


def test_executive_synthesis_preserves_execute_position():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication=(
                "Delivery is off track due to resource dependency."
            ),
            recommended_action=(
                "Remove the critical resource dependency."
            ),
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    course_correction = assess_course_correction(portfolio)

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
    )

    assert course_correction.action == "EXECUTE"
    assert executive_view.strategic_position == "EXECUTE"
    assert executive_view.confidence == course_correction.confidence

    assert "transform" not in executive_view.recommended_response.lower()
    assert "adapt" not in executive_view.recommended_response.lower()
    assert "reconsider" not in executive_view.recommended_response.lower()


def test_executive_synthesis_preserves_reconsider_position():
    from strategic_course_correction import StrategicThesisEvidence

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication=(
                "Evidence challenges the basis of the current growth strategy."
            ),
            recommended_action=(
                "Review the continued validity of the strategic thesis."
            ),
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required=(
                "Determine whether the current strategic thesis remains valid."
            ),
        ),
    ]

    portfolio = synthesise_portfolio(views)

    thesis_evidence = [
        StrategicThesisEvidence(
            thesis="Sustained market growth supports the current strategy.",
            status="INVALIDATED",
            evidence=(
                "Persistent structural market contraction undermines "
                "the strategic growth thesis."
            ),
            persistence="SUSTAINED",
            materiality="CRITICAL",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        thesis_evidence=thesis_evidence,
    )

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
    )

    assert course_correction.action == "RECONSIDER"
    assert executive_view.strategic_position == "RECONSIDER"
    assert executive_view.confidence == "HIGH"

    assert executive_view.decision_required
    assert "strategic" in executive_view.decision_required.lower()


def test_executive_synthesis_exposes_decision_traceability():
    from strategic_course_correction import StrategicThesisEvidence

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Growth strategy is under material pressure.",
            recommended_action="Review strategic thesis.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Determine whether the strategic thesis remains valid.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    thesis_evidence = [
        StrategicThesisEvidence(
            thesis="Sustained market growth supports the current strategy.",
            status="INVALIDATED",
            evidence="Persistent structural market contraction.",
            persistence="SUSTAINED",
            materiality="CRITICAL",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        thesis_evidence=thesis_evidence,
    )

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
        thesis_evidence=thesis_evidence,
    )

    assert executive_view.strategic_position == "RECONSIDER"

    assert executive_view.traceability
    assert executive_view.traceability.primary_issue == "DEMAND_WEAKNESS"
    assert executive_view.traceability.strategic_trigger == "STRATEGIC_THESIS"
    assert executive_view.traceability.trigger_evidence == (
        "Persistent structural market contraction."
    )
    assert executive_view.traceability.confidence == "HIGH"


def test_executive_traceability_identifies_strategic_assumption_trigger():
    from strategic_course_correction import StrategicAssumption

    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Growth objective is at risk.",
            recommended_action="Review market and proposition response.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assumptions = [
        StrategicAssumption(
            name="Market demand growth",
            assumption="Target market demand will continue to grow.",
            status="INVALIDATED",
            evidence="Market demand has contracted materially and persistently.",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        assumptions=assumptions,
    )

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
        assumptions=assumptions,
    )

    assert executive_view.strategic_position == "ADAPT"
    assert executive_view.traceability.strategic_trigger == "STRATEGIC_ASSUMPTION"
    assert executive_view.traceability.trigger_evidence == (
        "Market demand has contracted materially and persistently."
    )
    assert executive_view.traceability.confidence == "HIGH"


def test_executive_traceability_identifies_strategic_capability_trigger():
    from strategic_course_correction import StrategicCapabilityGap

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=["RESOURCE_DEPENDENCY"],
            confidence="HIGH",
            board_implication=(
                "Existing capability is insufficient to deliver "
                "the strategic objective."
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

    assert executive_view.strategic_position == "TRANSFORM"
    assert executive_view.traceability.strategic_trigger == "STRATEGIC_CAPABILITY"
    assert executive_view.traceability.trigger_evidence == (
        "Digital origination: Manual multi-stage processing "
        "-> Scalable straight-through processing"
    )
    assert executive_view.traceability.confidence == "HIGH"


def test_executive_traceability_identifies_strategic_dependency_trigger():
    from strategic_course_correction import StrategicDependency

    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=[],
            confidence="HIGH",
            board_implication=(
                "Delivery sequence is constrained by an unresolved dependency."
            ),
            recommended_action=(
                "Resolve the blocking dependency before continuing execution."
            ),
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    dependencies = [
        StrategicDependency(
            name="Core platform readiness",
            prerequisite="Core platform migration completed",
            dependent_objective="Digital origination deployment",
            status="BLOCKING",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        dependencies=dependencies,
    )

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
        dependencies=dependencies,
    )

    assert executive_view.strategic_position == "RESEQUENCE"
    assert executive_view.traceability.strategic_trigger == "STRATEGIC_DEPENDENCY"
    assert executive_view.traceability.trigger_evidence == (
        "Core platform readiness: Core platform migration completed "
        "-> Digital origination deployment"
    )
    assert executive_view.traceability.confidence == "HIGH"


def test_executive_traceability_identifies_execution_trigger():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication=(
                "Execution is constrained by an operational resource dependency."
            ),
            recommended_action=(
                "Resolve the execution constraint."
            ),
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    course_correction = assess_course_correction(portfolio)

    executive_view = synthesise_executive_strategy(
        portfolio,
        course_correction,
    )

    assert executive_view.strategic_position == "EXECUTE"
    assert executive_view.traceability.strategic_trigger == "EXECUTION"
    assert executive_view.traceability.trigger_evidence == (
        "RESOURCE_DEPENDENCY"
    )
    assert executive_view.traceability.confidence == course_correction.confidence
