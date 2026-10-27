from unittest.mock import patch

from board_intelligence import generate_board_intelligence


def test_decision_gate_evidence_reaches_adjudicator():
    evidence = {
        "test_marker": "MACIAN-EVIDENCE-FLOW-001"
    }

    policy = {
        "policy": "HOLD",
        "evidence": "Additional verification required",
    }

    def check_adjudicator(**kwargs):
        assert kwargs["decision_gate_inputs"] is evidence
        assert kwargs["document_text"] == "Test investment proposal"
        return {"status": "TESTED"}

    with (
        patch("board_orchestrator.analyse_document", return_value="Decision analysis"),
        patch("board_orchestrator.analyse_strategy", return_value="Strategy analysis"),
        patch("board_orchestrator.analyse_finance", return_value="Finance analysis"),
        patch("board_orchestrator.get_framework_guidance", return_value="Frameworks"),
        patch("board_orchestrator.synthesise_strategy", return_value="Synthesis"),
        patch("board_orchestrator.adjudicate_decision", side_effect=check_adjudicator) as adjudicator,
        patch("board_orchestrator.evaluate_decision_policy", return_value=policy),
        patch("board_intelligence.load_board_framework", return_value="Board framework"),
        patch("board_intelligence.analyse_document", return_value="Board report") as report,
    ):
        result = generate_board_intelligence(
            document_text="Test investment proposal",
            decision_gate_inputs=evidence,
        )

    assert result == "Board report"
    adjudicator.assert_called_once()
    report.assert_called_once()
    assert "HOLD" in report.call_args.args[0]
    assert "Additional verification required" in report.call_args.args[0]
