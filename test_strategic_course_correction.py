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


def test_structural_capability_gap_triggers_transform():
    from strategic_course_correction import StrategicCapabilityGap

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="PROCESS_CAPACITY_CONSTRAINT",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication="The current operating capability cannot support strategic scale.",
            recommended_action="Address structural capability constraints.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve operating capability transformation.",
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

    assert course_correction.action == "TRANSFORM"
    assert course_correction.strategy_challenge is False
    assert "capability" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"


def test_non_structural_capability_gap_does_not_trigger_transform():
    from strategic_course_correction import StrategicCapabilityGap

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Technology delivery is off track.",
            recommended_action="Recover technology delivery.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    capability_gaps = [
        StrategicCapabilityGap(
            capability="Digital origination",
            required_state="Scalable straight-through processing",
            current_state="Current platform requires remediation",
            gap_type="EXECUTION",
            persistence="SUSTAINED",
            materiality="HIGH",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        capability_gaps=capability_gaps,
    )

    assert course_correction.action == "EXECUTE"
    assert course_correction.strategy_challenge is False


def test_invalidated_strategic_thesis_triggers_reconsider():
    from strategic_course_correction import StrategicThesis

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=["COMMERCIAL_CONVERSION_WEAKNESS"],
            confidence="HIGH",
            board_implication="The growth strategy is materially underperforming.",
            recommended_action="Review the strategic proposition.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Determine whether the current strategic thesis remains viable.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    theses = [
        StrategicThesis(
            name="Profitable market expansion",
            thesis=(
                "The target market can support profitable growth "
                "at the required scale."
            ),
            status="INVALIDATED",
            evidence=(
                "Sustained market contraction and adverse unit economics "
                "challenge the viability of the growth thesis."
            ),
            materiality="CRITICAL",
            persistence="SUSTAINED",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        theses=theses,
    )

    assert course_correction.action == "RECONSIDER"
    assert course_correction.strategy_challenge is True
    assert "thesis" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"


def test_non_critical_thesis_does_not_trigger_reconsider():
    from strategic_course_correction import StrategicThesis

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Growth performance is materially under pressure.",
            recommended_action="Review strategic response.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Review strategic response.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    theses = [
        StrategicThesis(
            name="Profitable market expansion",
            thesis="The target market can support profitable growth.",
            status="INVALIDATED",
            evidence="Evidence challenges elements of the growth thesis.",
            materiality="HIGH",
            persistence="SUSTAINED",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        theses=theses,
    )

    assert course_correction.action == "EXECUTE"
    assert course_correction.strategy_challenge is False


def test_invalidated_strategic_thesis_triggers_reconsider():
    from strategic_course_correction import StrategicThesisEvidence

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="The strategic growth thesis is under material pressure.",
            recommended_action="Review strategic direction.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Review continued strategic commitment.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    thesis_evidence = [
        StrategicThesisEvidence(
            thesis="Sustained growth in the target market creates an attractive basis for investment.",
            status="INVALIDATED",
            evidence="Structural market contraction has removed the economic basis for the planned growth strategy.",
            persistence="SUSTAINED",
            materiality="CRITICAL",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        thesis_evidence=thesis_evidence,
    )

    assert course_correction.action == "RECONSIDER"
    assert course_correction.strategy_challenge is True
    assert "thesis" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"


def test_non_critical_thesis_evidence_does_not_trigger_reconsider():
    from strategic_course_correction import StrategicThesisEvidence

    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="DEMAND_WEAKNESS",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="The growth strategy is under pressure.",
            recommended_action="Review market response.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    thesis_evidence = [
        StrategicThesisEvidence(
            thesis="Target market supports sustained growth.",
            status="INVALIDATED",
            evidence="Market conditions have weakened materially.",
            persistence="SUSTAINED",
            materiality="HIGH",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        thesis_evidence=thesis_evidence,
    )

    assert course_correction.action != "RECONSIDER"
    assert course_correction.strategy_challenge is False


def test_structural_capability_gap_triggers_transform():
    from strategic_course_correction import StrategicCapabilityGap

    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="PROCESS_CAPACITY_CONSTRAINT",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication="Current operating capability cannot support strategic scale.",
            recommended_action="Address structural capability constraints.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve structural capability intervention.",
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

    assert course_correction.action == "TRANSFORM"
    assert course_correction.strategy_challenge is False
    assert "capability" in course_correction.rationale.lower()
    assert course_correction.confidence == "HIGH"
