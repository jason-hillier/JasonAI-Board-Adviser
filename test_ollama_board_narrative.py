from board_briefing_generator import BoardBriefing

from ollama_board_narrative import build_board_narrative_prompt


def test_board_narrative_prompt_contains_governed_context():
    briefing = BoardBriefing(
        strategic_position="TRANSFORM",
        confidence="HIGH",
        executive_summary="Structural capability is insufficient.",
        board_implication="Current capability cannot deliver the strategy.",
        recommended_response="Transform the underlying capability.",
        decision_required="Approve structural capability intervention.",
        supporting_evidence="Structural capability gap confirmed.",
    )

    prompt = build_board_narrative_prompt(briefing)

    assert "TRANSFORM" in prompt
    assert "HIGH" in prompt
    assert "Structural capability gap confirmed." in prompt
    assert "Approve structural capability intervention." in prompt

    assert "executive_summary" in prompt
    assert "board_implication" in prompt
    assert "recommended_response" in prompt

    assert "Do not change" in prompt


def test_parse_board_narrative_response_accepts_valid_json():
    from ollama_board_narrative import parse_board_narrative_response

    response = """
    {
      "executive_summary": "The strategy requires structural transformation.",
      "board_implication": "Current capability is insufficient to deliver the strategic objective sustainably.",
      "recommended_response": "Transform the underlying capability while preserving the strategic intent."
    }
    """

    narrative = parse_board_narrative_response(response)

    assert narrative == {
        "executive_summary": (
            "The strategy requires structural transformation."
        ),
        "board_implication": (
            "Current capability is insufficient to deliver the "
            "strategic objective sustainably."
        ),
        "recommended_response": (
            "Transform the underlying capability while preserving "
            "the strategic intent."
        ),
    }


def test_parse_board_narrative_response_rejects_governed_fields():
    import pytest

    from ollama_board_narrative import parse_board_narrative_response

    response = """
    {
      "executive_summary": "Enhanced executive summary.",
      "board_implication": "Enhanced Board implication.",
      "recommended_response": "Enhanced recommended response.",
      "strategic_position": "EXECUTE"
    }
    """

    with pytest.raises(ValueError):
        parse_board_narrative_response(response)


def test_generate_board_narrative_uses_model_and_returns_valid_narrative():
    from ollama_board_narrative import generate_board_narrative

    briefing = BoardBriefing(
        strategic_position="TRANSFORM",
        confidence="HIGH",
        executive_summary="Structural capability is insufficient.",
        board_implication="Current capability cannot deliver the strategy.",
        recommended_response="Transform the underlying capability.",
        decision_required="Approve structural capability intervention.",
        supporting_evidence="Structural capability gap confirmed.",
    )

    class FakeOllamaClient:
        def chat(self, **kwargs):
            assert kwargs["model"] == "llama3.1"
            assert kwargs["format"] == "json"

            return {
                "message": {
                    "content": """
                    {
                      "executive_summary": "Structural transformation is required to protect delivery of the strategic objective.",
                      "board_implication": "The current operating capability cannot sustainably support the required strategic outcome.",
                      "recommended_response": "Transform the underlying capability while preserving the strategic intent."
                    }
                    """
                }
            }

    narrative = generate_board_narrative(
        briefing,
        client=FakeOllamaClient(),
        model="llama3.1",
    )

    assert narrative["executive_summary"]
    assert narrative["board_implication"]
    assert narrative["recommended_response"]

    assert set(narrative.keys()) == {
        "executive_summary",
        "board_implication",
        "recommended_response",
    }
