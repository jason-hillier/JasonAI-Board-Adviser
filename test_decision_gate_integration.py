import pytest
from unittest.mock import patch

from decision_adjudicator import adjudicate_decision


def test_adjudicator_rejects_missing_gate_evidence():
    with patch("decision_adjudicator.ollama.chat") as mock_chat:
        with pytest.raises(
            ValueError,
            match="Missing or invalid decision gate evidence",
        ):
            adjudicate_decision(
                document_text="Test investment proposal",
                decision_analysis="Analysis",
                strategy_analysis="Strategy",
                finance_analysis="Finance",
                strategic_synthesis="Synthesis",
                decision_gate_inputs={},
            )

        mock_chat.assert_not_called()
