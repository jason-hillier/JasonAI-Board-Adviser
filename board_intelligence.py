from pathlib import Path

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
        The Decision Engine performs the core strategic analysis.

    Stage 2:
        The Board Framework converts that analysis into a structured
        board-ready report.
    """

    if not document_text or not document_text.strip():
        raise ValueError("No document text was supplied.")

    decision_analysis = analyse_document(document_text)
    board_framework = load_board_framework()

    final_input = f"""
Apply the following Board Intelligence Framework to the Decision Engine analysis.

BOARD INTELLIGENCE FRAMEWORK:
{board_framework}

DECISION ENGINE ANALYSIS:
{decision_analysis}

Produce a concise, rigorous and board-ready report.

Requirements:
- Do not invent facts.
- Distinguish facts, assumptions and inferences.
- Highlight missing evidence.
- Explain the basis for the confidence score.
- End with a clear Board recommendation.
"""

    return analyse_document(final_input)