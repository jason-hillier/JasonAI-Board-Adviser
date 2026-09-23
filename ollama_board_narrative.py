from board_briefing_generator import BoardBriefing


def build_board_narrative_prompt(
    briefing: BoardBriefing,
) -> str:
    """
    Build the governed prompt used for Board narrative enhancement.

    The language model may improve narrative quality only.
    It must not alter governed strategic intelligence.
    """

    return f"""
You are a strategic adviser preparing concise Board-level narrative.

The strategic analysis below has already been determined by a governed
decision engine. Treat these fields as authoritative facts.

GOVERNED STRATEGIC INTELLIGENCE

Strategic position: {briefing.strategic_position}
Confidence: {briefing.confidence}
Decision required: {briefing.decision_required}
Supporting evidence: {briefing.supporting_evidence}

CURRENT NARRATIVE

Executive summary:
{briefing.executive_summary}

Board implication:
{briefing.board_implication}

Recommended response:
{briefing.recommended_response}

TASK

Improve the quality, precision and executive clarity of the narrative
for a Board audience.

Do not change, reinterpret, contradict, weaken or strengthen:
- the strategic position
- confidence
- the decision required
- supporting evidence

Do not introduce new facts, evidence, causes, assumptions or conclusions.

Return only valid JSON with exactly these three fields:

{{
  "executive_summary": "...",
  "board_implication": "...",
  "recommended_response": "..."
}}
""".strip()


def parse_board_narrative_response(
    response: str,
) -> dict:
    """
    Parse and validate narrative output from the local language model.

    Only the three authorised narrative fields are permitted.
    Governed strategic fields must never be accepted from the model.
    """
    import json

    allowed_fields = {
        "executive_summary",
        "board_implication",
        "recommended_response",
    }

    try:
        narrative = json.loads(response)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("Invalid Board narrative JSON") from exc

    if not isinstance(narrative, dict):
        raise ValueError("Board narrative response must be a JSON object")

    if set(narrative.keys()) != allowed_fields:
        raise ValueError(
            "Board narrative response contains missing or unauthorised fields"
        )

    for field in allowed_fields:
        value = narrative[field]

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Board narrative field '{field}' must be non-empty text"
            )

    return narrative


def generate_board_narrative(
    briefing: BoardBriefing,
    client=None,
    model: str = "llama3.1",
) -> dict:
    """
    Generate Board-level narrative using a local Ollama model.

    The model receives governed strategic intelligence but may return
    only the three authorised narrative fields. All output is validated
    before being returned.
    """

    if client is None:
        import ollama
        client = ollama.Client()

    prompt = build_board_narrative_prompt(briefing)

    response = client.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format="json",
        options={
            "temperature": 0.2,
        },
    )

    try:
        content = response["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "Invalid response received from Ollama"
        ) from exc

    return parse_board_narrative_response(content)
