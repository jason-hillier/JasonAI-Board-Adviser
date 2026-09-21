from board_strategic_synthesis import BoardStrategicView
from board_portfolio_intelligence import synthesise_portfolio

from strategic_course_correction import assess_course_correction


def test_execution_failure_does_not_automatically_trigger_strategy_change():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Strategic delivery is constrained by resource dependency.",
            recommended_action="Remove critical resource dependency.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve additional capacity.",
        ),
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="PROCESS_CAPACITY_CONSTRAINT",
            contributing_causes=["RESOURCE_DEPENDENCY"],
            confidence="HIGH",
            board_implication="Operational delivery is constrained.",
            recommended_action="Address capacity constraints.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    course_correction = assess_course_correction(portfolio)

    assert course_correction.action == "EXECUTE"
    assert course_correction.strategy_challenge is False
    assert course_correction.rationale
    assert course_correction.confidence == "HIGH"


def test_invalidated_strategic_assumption_triggers_adaptation():
    from strategic_course_correction import StrategicAssumption

    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Growth objective is at risk due to weaker demand.",
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

    assert course_correction.action == "ADAPT"
    assert course_correction.strategy_challenge is True
    assert "assumption" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"


def test_low_confidence_invalidated_assumption_does_not_trigger_adaptation():
    from strategic_course_correction import StrategicAssumption

    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="MODERATE",
            board_implication="Growth objective is at risk.",
            recommended_action="Review market conditions.",
            escalation_level="ATTENTION",
            board_ask="ATTENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assumptions = [
        StrategicAssumption(
            name="Market demand growth",
            assumption="Target market demand will continue to grow.",
            status="INVALIDATED",
            evidence="Early indicators suggest demand may be weakening.",
            confidence="LOW",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        assumptions=assumptions,
    )

    assert course_correction.action == "EXECUTE"
    assert course_correction.strategy_challenge is False


def test_material_strategic_dependency_triggers_resequence():
    from strategic_course_correction import StrategicDependency

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication="Multiple strategic objectives compete for constrained capacity.",
            recommended_action="Resolve portfolio sequencing and capacity.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve revised strategic sequencing.",
        ),
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=["RESOURCE_DEPENDENCY"],
            confidence="HIGH",
            board_implication="Technology dependency threatens downstream delivery.",
            recommended_action="Resequence dependent delivery.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    dependencies = [
        StrategicDependency(
            name="Platform before growth",
            prerequisite="Core platform capability",
            dependent_objective="Growth acceleration",
            status="BLOCKING",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        dependencies=dependencies,
    )

    assert course_correction.action == "RESEQUENCE"
    assert course_correction.strategy_challenge is False
    assert "sequenc" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"


def test_invalidated_assumption_takes_precedence_over_blocking_dependency():
    from strategic_course_correction import (
        StrategicAssumption,
        StrategicDependency,
    )

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=["RESOURCE_DEPENDENCY"],
            confidence="HIGH",
            board_implication="Growth strategy is under pressure.",
            recommended_action="Review strategic response.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve strategic response.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assumptions = [
        StrategicAssumption(
            name="Market demand growth",
            assumption="Target market demand will continue to grow.",
            status="INVALIDATED",
            evidence="Demand has contracted materially and persistently.",
            confidence="HIGH",
        ),
    ]

    dependencies = [
        StrategicDependency(
            name="Platform before growth",
            prerequisite="Core platform capability",
            dependent_objective="Growth acceleration",
            status="BLOCKING",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        assumptions=assumptions,
        dependencies=dependencies,
    )

    assert course_correction.action == "ADAPT"
    assert course_correction.strategy_challenge is True
    assert course_correction.confidence == "HIGH"
