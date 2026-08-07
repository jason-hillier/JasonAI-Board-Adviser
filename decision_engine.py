from pathlib import Path

import ollama


PROJECT_ROOT = Path(__file__).resolve().parent
DECISION_PROMPT_PATH = PROJECT_ROOT / "prompts" / "decision_engine.txt"

DEFAULT_MODEL = "llama3.1:latest"


def load_decision_prompt() -> str:
    """
    Load Macian's core decision-engine instructions.
    """

    if not DECISION_PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Decision-engine prompt not found: {DECISION_PROMPT_PATH}"
        )

    prompt = DECISION_PROMPT_PATH.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError("The decision-engine prompt is empty.")

    return prompt


def analyse_document(
    document_text: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Analyse document text using Macian's decision framework.
    """

    if not document_text or not document_text.strip():
        raise ValueError("No document text was supplied for analysis.")

    system_prompt = load_decision_prompt()

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    "Analyse the following document using the Macian "
                    "Decision Engine.\n\n"
                    "Base conclusions only on the supplied evidence. "
                    "Clearly identify missing information and uncertainty.\n\n"
                    f"DOCUMENT:\n{document_text}"
                ),
            },
        ],
    )

    output = response["message"]["content"].strip()

    if not output:
        raise RuntimeError("Ollama returned an empty response.")

    return output