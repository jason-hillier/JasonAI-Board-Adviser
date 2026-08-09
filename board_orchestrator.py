from decision_engine import analyse_document
from agents.strategy_agent import analyse_strategy
from agents.finance_agent import analyse_finance


def run_board_orchestration(document_text: str) -> dict:
    """
    Run Macian's specialist analyses and return their outputs.

    The orchestrator coordinates agents.
    It does not make the final Board decision.
    """

    if not document_text or not document_text.strip():
        raise ValueError("No document text supplied to Board Orchestrator.")

    decision_analysis = analyse_document(document_text)
    strategy_analysis = analyse_strategy(document_text)
    finance_analysis = analyse_finance(document_text)

    return {
        "decision_analysis": decision_analysis,
        "strategy_analysis": strategy_analysis,
        "finance_analysis": finance_analysis,
    }