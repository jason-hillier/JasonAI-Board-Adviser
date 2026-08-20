from pathlib import Path

from board_orchestrator import run_board_orchestration
from decision_engine import analyse_document

PROJECT_ROOT = Path(__file__).resolve().parent
BOARD_FRAMEWORK_PATH = PROJECT_ROOT / "prompts" / "board_framework.txt"


def load_board_framework() -> str:
    """
    Load Macian's board intelligence reporting framework.
    """

    if not BOARD_FRAMEWORK_PATH.exists():
        raise FileNotFoundError(
            f"Board framework prompt not found: {BOARD_FRAMEWORK_PATH}"
        )

    framework = BOARD_FRAMEWORK_PATH.read_text(encoding="utf-8").strip()

    if not framework:
        raise ValueError("The board framework prompt is empty.")

    return framework


def generate_board_intelligence(document_text: str) -> str:
    """
    Generate a board-level executive intelligence report.

Stage 1:
    The Board Orchestrator coordinates specialist analysis.

Stage 2:
    The Board Framework synthesises the specialist analyses into a
    structured, board-ready intelligence report.
    """

    if not document_text or not document_text.strip():
        raise ValueError("No document text was supplied.")

    orchestration = run_board_orchestration(document_text)

    decision_analysis = orchestration.get("decision_analysis")
    strategy_analysis = orchestration.get("strategy_analysis")
    finance_analysis = orchestration.get ("finance_analysis")
    strategic_frameworks = orchestration["strategic_frameworks"]
    decision_policy = orchestration["decision_policy"]

    board_framework = load_board_framework()

    final_input = f"""

Apply the following Board Intelligence Framework to the Decision Engine analysis.

BOARD INTELLIGENCE FRAMEWORK:
{board_framework}

DECISION ENGINE ANALYSIS:
{decision_analysis}

STRATEGY AGENT ANALYSIS:
{strategy_analysis}

FINANCE AGENT ANALYSIS:
{finance_analysis}

SELECTED STRATEGIC FRAMEWORKS:
{strategic_frameworks}

Apply these frameworks selectively to challenge the proposal.
Do not merely describe or name the frameworks.
Use them to identify decision-relevant implications, contradictions,
alternatives, opportunity costs and strategic risks.

CROSS-AGENT CHALLENGE:

Do not simply aggregate or summarise the agent analyses.

Identify where the Strategy Agent, Finance Agent and Decision Engine:
- agree and reinforce one another;
- disagree or reach conflicting conclusions;
- rely on different assumptions;
- identify evidence of different strength or quality.

Where analyses conflict, adjudicate between them using the available
evidence and explain which conclusion should carry greater weight and why.

Identify any material issue that has been overlooked by all agents.

DECISION OPTIONS:

Do not treat the decision as simply approve versus reject.

Where appropriate, identify credible alternative courses of action,
including defer, pilot, phase, redesign, renegotiate, competitively tender,
or approve subject to explicit conditions.

For each credible option, consider:
- strategic value;
- financial exposure;
- reversibility;
- opportunity cost;
- execution risk;
- evidence required before further commitment.

Prefer staged or reversible decisions where uncertainty is high and
additional evidence can be obtained at reasonable cost.

The Board recommendation must identify the preferred course of action
and explain why it is superior to the principal alternatives.

DECISION POLICY:
{decision_policy["policy"]}

POLICY EVIDENCE:
{decision_policy["evidence"]}

Produce a concise, rigorous and board-ready report.

Requirements:
- The final Board recommendation must comply with the Decision Policy.
- Do not treat adverse evidence as merely missing evidence.
- Do not invent facts.
- Distinguish facts, assumptions and inferences.
- Highlight missing evidence.
- Explain the basis for the confidence score.
- End with a clear Board recommendation.
"""

    return analyse_document(final_input)