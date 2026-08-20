from decision_engine import analyse_document
from agents.strategy_agent import analyse_strategy
from agents.finance_agent import analyse_finance
from decision_policy import evaluate_decision_policy
from strategic_framework_engine import get_framework_guidance
from strategic_synthesis import synthesise_strategy
from decision_adjudicator import adjudicate_decision

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
    strategic_frameworks = get_framework_guidance(document_text)
    strategic_synthesis = synthesise_strategy(
    document_text=document_text,
    decision_analysis=decision_analysis,
    strategy_analysis=strategy_analysis,
    finance_analysis=finance_analysis,
    strategic_frameworks=strategic_frameworks,
    )

    decision_adjudication = adjudicate_decision(
    document_text=document_text,
    decision_analysis=decision_analysis,
    strategy_analysis=strategy_analysis,
    finance_analysis=finance_analysis,
    strategic_synthesis=strategic_synthesis,
)
    
    decision_policy = evaluate_decision_policy(
    document_text=document_text,
    decision_analysis=decision_analysis,
    strategy_analysis=strategy_analysis,
    finance_analysis=finance_analysis,
)

    return {
        "decision_analysis": decision_analysis,
        "strategy_analysis": strategy_analysis,
        "finance_analysis": finance_analysis,
        "strategic_frameworks": strategic_frameworks,
        "strategic_synthesis": strategic_synthesis,
        "decision_adjudication": decision_adjudication,
        "decision_policy": decision_policy,
    }