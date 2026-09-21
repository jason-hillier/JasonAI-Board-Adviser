from board_strategic_synthesis import BoardStrategicView
from board_portfolio_intelligence import synthesise_portfolio
from strategic_course_correction import (
    StrategicCapabilityGap,
    assess_course_correction,
)

from executive_strategic_synthesis import synthesise_executive_view


def test_executive_synthesis_combines_portfolio_and_course_correction():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication="Strategic delivery is constrained.",
            recommended_action="Remove critical resource dependency.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve enterprise capacity intervention.",
        ),
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Operational delivery is constrained.",
            recommended_action="Address resource dependency.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    capability_gaps = [
        StrategicCapabilityGap(
            capability="Enterprise delivery capacity",
            required_state="Scalable cross-portfolio delivery capability",
            current_state="Persistent critical resource dependencies",
            gap_type="STRUCTURAL",
            persistence="SUSTAINED",
            materiality="CRITICAL",
            confidence="HIGH",
        ),
    ]

    course_correction = assess_course_correction(
        portfolio,
        capability_gaps=capability_gaps,
    )

    executive_view = synthesise_executive_view(
        portfolio,
        course_correction,
    )

    assert executive_view.strategic_position == "OFF_TRACK"
    assert executive_view.course_of_action == "TRANSFORM"
    assert "RESOURCE_DEPENDENCY" in executive_view.systemic_constraints
    assert executive_view.priority_issue == "RESOURCE_DEPENDENCY"
    assert executive_view.board_decision
    assert "approve" in executive_view.board_decision.lower()
    assert "resource" in executive_view.board_decision.lower()
    assert executive_view.rationale
    assert executive_view.confidence == "HIGH"


def test_executive_synthesis_elevates_systemic_portfolio_decision():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Transformation delivery is constrained.",
            recommended_action="Remove local resource dependency.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve additional programme resource.",
        ),
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Operational delivery is constrained.",
            recommended_action="Address resource dependency.",
            escalation_level="INTERVENTION",
            board_ask="INTERVENTION",
            decision_required=None,
        ),
    ]

    portfolio = synthesise_portfolio(views)

    course_correction = assess_course_correction(portfolio)

    executive_view = synthesise_executive_view(
        portfolio,
        course_correction,
    )

    assert "RESOURCE_DEPENDENCY" in executive_view.systemic_constraints
    assert "enterprise" in executive_view.board_decision.lower()
    assert "resource" in executive_view.board_decision.lower()
