from board_briefing_generator import BoardBriefing
from board_narrative_enhancer import enhance_board_narrative


def test_narrative_enhancement_preserves_governed_fields():
    briefing = BoardBriefing(
        strategic_position="TRANSFORM",
        confidence="HIGH",
        executive_summary=(
            "Strategic position: TRANSFORM. "
            "Structural capability is insufficient."
        ),
        board_implication=(
            "Current capability cannot sustainably deliver the strategy."
        ),
        recommended_response=(
            "Transform the underlying organisational capability."
        ),
        decision_required=(
            "Approve structural capability intervention."
        ),
        supporting_evidence=(
            "Digital origination: Manual processing "
            "-> Scalable straight-through processing"
        ),
    )

    enhanced = enhance_board_narrative(briefing)

    assert enhanced.strategic_position == "TRANSFORM"
    assert enhanced.confidence == "HIGH"
    assert enhanced.decision_required == (
        "Approve structural capability intervention."
    )
    assert enhanced.supporting_evidence == (
        "Digital origination: Manual processing "
        "-> Scalable straight-through processing"
    )

    assert enhanced.executive_summary
    assert enhanced.board_implication
    assert enhanced.recommended_response


def test_narrative_enhancement_falls_back_to_original_briefing():
    briefing = BoardBriefing(
        strategic_position="ADAPT",
        confidence="HIGH",
        executive_summary="Original executive summary.",
        board_implication="Original Board implication.",
        recommended_response="Original recommended response.",
        decision_required="Approve adaptation of the strategic approach.",
        supporting_evidence="A strategic assumption has been invalidated.",
    )

    enhanced = enhance_board_narrative(
        briefing,
        narrative_generator=lambda _: None,
    )

    assert enhanced == briefing


def test_narrative_generator_cannot_change_governed_fields():
    briefing = BoardBriefing(
        strategic_position="TRANSFORM",
        confidence="HIGH",
        executive_summary="Original executive summary.",
        board_implication="Original Board implication.",
        recommended_response="Original recommended response.",
        decision_required="Approve structural capability intervention.",
        supporting_evidence="Structural capability gap confirmed.",
    )

    def hostile_generator(_):
        return {
            # Legitimate narrative enhancements
            "executive_summary": "Enhanced executive summary.",
            "board_implication": "Enhanced Board implication.",
            "recommended_response": "Enhanced recommended response.",

            # Attempted changes to governed intelligence
            "strategic_position": "EXECUTE",
            "confidence": "LOW",
            "decision_required": "No Board decision required.",
            "supporting_evidence": "Different evidence.",
        }

    enhanced = enhance_board_narrative(
        briefing,
        narrative_generator=hostile_generator,
    )

    # Narrative fields may be enhanced
    assert enhanced.executive_summary == "Enhanced executive summary."
    assert enhanced.board_implication == "Enhanced Board implication."
    assert enhanced.recommended_response == "Enhanced recommended response."

    # Governed fields must remain immutable
    assert enhanced.strategic_position == "TRANSFORM"
    assert enhanced.confidence == "HIGH"
    assert enhanced.decision_required == (
        "Approve structural capability intervention."
    )
    assert enhanced.supporting_evidence == (
        "Structural capability gap confirmed."
    )


def test_narrative_enhancer_integrates_governed_ollama_generator():
    from ollama_board_narrative import generate_board_narrative

    briefing = BoardBriefing(
        strategic_position="TRANSFORM",
        confidence="HIGH",
        executive_summary="Original executive summary.",
        board_implication="Original Board implication.",
        recommended_response="Original recommended response.",
        decision_required="Approve structural capability intervention.",
        supporting_evidence="Structural capability gap confirmed.",
    )

    class FakeOllamaClient:
        def chat(self, **kwargs):
            return {
                "message": {
                    "content": """
                    {
                      "executive_summary": "The strategic objective remains valid, but delivery requires structural transformation.",
                      "board_implication": "Current organisational capability is insufficient to sustain delivery of the strategic objective.",
                      "recommended_response": "Transform the underlying capability while preserving the strategic intent."
                    }
                    """
                }
            }

    client = FakeOllamaClient()

    def generator(governed_briefing):
        return generate_board_narrative(
            governed_briefing,
            client=client,
            model="llama3.1",
        )

    enhanced = enhance_board_narrative(
        briefing,
        narrative_generator=generator,
    )

    # LLM narrative accepted
    assert "structural transformation" in enhanced.executive_summary.lower()
    assert "organisational capability" in enhanced.board_implication.lower()

    # Governed intelligence remains immutable
    assert enhanced.strategic_position == "TRANSFORM"
    assert enhanced.confidence == "HIGH"
    assert enhanced.decision_required == (
        "Approve structural capability intervention."
    )
    assert enhanced.supporting_evidence == (
        "Structural capability gap confirmed."
    )
