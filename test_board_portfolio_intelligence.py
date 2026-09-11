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
