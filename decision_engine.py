from pathlib import Path

import ollama

import json

from decision_models import DecisionCase, EvidenceItem, Finding, Risk, Opportunity, TradeOff, DecisionOption

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
  ],
  "opportunities": [
    {
      "title": "string",
      "description": "string",
      "materiality": "LOW | MEDIUM | HIGH",
      "strategic_value": "LOW | MEDIUM | HIGH",
      "evidence_type": "FACT | ASSUMPTION | INFERENCE | GAP",
      "source": null
    }
  ],
  "tradeoffs": [
    {
      "title": "string",
      "description": "string",
      "benefit": "string",
      "cost": "string",
      "materiality": "LOW | MEDIUM | HIGH"
    }
  ],
  "options": [
    {
      "name": "string",
      "description": "string",
      "strategic_value": "LOW | MEDIUM | HIGH",
      "downside_exposure": "LOW | MEDIUM | HIGH",
      "reversibility": "LOW | MEDIUM | HIGH",
      "execution_risk": "LOW | MEDIUM | HIGH",
      "opportunity_cost": "LOW | MEDIUM | HIGH",
      "evidence_required": null
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

    def _parse_structured_json(raw_output: str):
        cleaned = raw_output.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        json_start = cleaned.find("{")
        if json_start == -1:
            raise json.JSONDecodeError(
                "No JSON object found",
                cleaned,
                0,
            )

        decoder = json.JSONDecoder()
        result, _ = decoder.raw_decode(cleaned[json_start:])

        if not isinstance(result, dict):
            raise ValueError(
                "Structured decision response must be a JSON object."
            )

        return result

    try:
        result = _parse_structured_json(output)

    except (json.JSONDecodeError, ValueError):
        repair_response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a JSON repair engine. "
                        "Return one valid JSON object only. "
                        "Do not add markdown or commentary. "
                        "Preserve the meaning and structure of the supplied data."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Repair the following malformed JSON so that it is "
                        "valid JSON. Return JSON only.\n\n"
                        + output
                    ),
                },
            ],
        )

        repaired_output = (
            repair_response["message"]["content"].strip()
        )

        if not repaired_output:
            raise RuntimeError(
                "Ollama returned an empty JSON repair response."
            )

        try:
            result = _parse_structured_json(repaired_output)
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                "Ollama failed to return valid structured JSON "
                "after one repair attempt."
            ) from exc

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

    opportunity_items = [
        Opportunity(**item)
        for item in result.get("opportunities", [])
    ]

    tradeoff_items = [
        TradeOff(
            title=item.get("title", "Untitled Trade-Off"),
            description=item.get("description", ""),
            benefit=item.get("benefit", ""),
            cost=item.get("cost", ""),
            materiality=item.get("materiality", "MEDIUM"),
        )
        for item in result.get("tradeoffs", [])
   ]

    option_items = [
    DecisionOption(
        name=item.get("name", "Untitled Option"),
        description=item.get("description", ""),
        strategic_value=item.get("strategic_value", "MEDIUM"),
        downside_exposure=item.get("downside_exposure", "MEDIUM"),
        reversibility=item.get("reversibility", "MEDIUM"),
        execution_risk=item.get("execution_risk", "MEDIUM"),
        opportunity_cost=item.get("opportunity_cost", "MEDIUM"),
        evidence_required=item.get("evidence_required"),
    )
    for item in result.get("options", [])
]

    return DecisionCase(
        title="Untitled Decision",
        proposal=document_text,
        evidence=evidence_items,
        findings=finding_items,
        risks=risk_items,
        opportunities=opportunity_items,
        tradeoffs=tradeoff_items,
        options=option_items,
        recommendation=None,
    )