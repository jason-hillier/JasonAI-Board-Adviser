from board_strategic_synthesis import BoardStrategicView
from board_portfolio_intelligence import synthesise_portfolio


def test_portfolio_identifies_highest_priority_board_issue():
    views = [
        BoardStrategicView(
            trajectory="AT_RISK",
            primary_cause="COMMERCIAL_CONVERSION_WEAKNESS",
            contributing_causes=[],
            confidence="MODERATE",
            board_implication="Commercial performance is at risk.",
            recommended_action="Address conversion weakness.",
            escalation_level="ATTENTION",
            board_ask="ATTENTION",
            decision_required=None,
        ),
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=["TECHNOLOGY_DELIVERY_CONSTRAINT"],
            confidence="HIGH",
            board_implication="Strategic delivery is off track due to resource dependency.",
            recommended_action="Remove critical resource dependencies.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve executive action to remove critical resource dependencies.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assert portfolio.priority_issue.primary_cause == "RESOURCE_DEPENDENCY"
    assert portfolio.priority_issue.trajectory == "OFF_TRACK"


def test_portfolio_prioritises_board_decision_over_intervention():
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
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Critical resource dependency threatens delivery.",
            recommended_action="Remove critical resource dependency.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve additional executive resource capacity.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assert portfolio.priority_issue.primary_cause == "RESOURCE_DEPENDENCY"
    assert portfolio.priority_issue.board_ask == "DECISION"


def test_portfolio_uses_confidence_to_break_equal_priority():
    views = [
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="TECHNOLOGY_DELIVERY_CONSTRAINT",
            contributing_causes=[],
            confidence="LOW",
            board_implication="Technology delivery may threaten the strategy.",
            recommended_action="Investigate technology delivery.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve technology recovery action.",
        ),
        BoardStrategicView(
            trajectory="OFF_TRACK",
            primary_cause="RESOURCE_DEPENDENCY",
            contributing_causes=[],
            confidence="HIGH",
            board_implication="Critical resource dependency threatens delivery.",
            recommended_action="Remove critical resource dependency.",
            escalation_level="DECISION",
            board_ask="DECISION",
            decision_required="Approve additional executive resource capacity.",
        ),
    ]

    portfolio = synthesise_portfolio(views)

    assert portfolio.priority_issue.primary_cause == "RESOURCE_DEPENDENCY"
    assert portfolio.priority_issue.confidence == "HIGH"
