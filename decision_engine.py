from pathlib import Path

import ollama

import json

from decision_models import DecisionCase, EvidenceItem, Finding, Risk

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
        format="json",
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

def analyse_document_structured(
    document_text: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Analyse document text and return structured decision-engine output.
    """

    if not document_text or not document_text.strip():
        raise ValueError("No document text was supplied for analysis.")

    system_prompt = load_decision_prompt()

    structured_instruction = """
Return valid JSON only.

Use this exact structure:

{
  "evidence": [
    {
      "statement": "string",
      "evidence_type": "FACT | ASSUMPTION | INFERENCE | GAP",
      "materiality": "LOW | MEDIUM | HIGH",
      "source": null,
      "confidence": null
    }
  ],
  "findings": [
    {
      "title": "string",
      "description": "string",
      "materiality": "LOW | MEDIUM | HIGH",
      "evidence_type": "FACT | ASSUMPTION | INFERENCE | GAP",
      "source": null
    }
  ],
 "risks": [
    {
    "title": "string",
    "description": "string",
    "materiality": "LOW | MEDIUM | HIGH",
    "likelihood": "LOW | MEDIUM | HIGH",
    "impact": "LOW | MEDIUM | HIGH",
    "source": null
  }
]
}

Do not add markdown.
Do not add commentary outside the JSON.
Do not invent facts.
"""

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt + "\n\n" + structured_instruction,
            },
            {
                "role": "user",
                "content": (
                    "Analyse the following document using the Macian Decision Engine.\n\n"
                    f"DOCUMENT:\n{document_text}"
                ),
            },
        ],
    )

    output = response["message"]["content"].strip()

    if not output:
        raise RuntimeError("Ollama returned an empty structured response.")

    decoder = json.JSONDecoder()
    result, _ = decoder.raw_decode(output.lstrip())

    evidence_items = [
    EvidenceItem(**item)
    for item in result.get("evidence", [])
]

    finding_items = [
    Finding(**item)
    for item in result.get("findings", [])
]

    risk_items = [
    Risk(**item)
    for item in result.get("risks", [])
]

    return DecisionCase(
    title="Untitled Decision",
    proposal=document_text,
    evidence=evidence_items,
    findings=finding_items,
    risks=risk_items,
    opportunities=[],
    tradeoffs=[],
    options=[],
    recommendation=None,
)