from narrative_governance import validate_narrative_language


def test_rejects_unsupported_existential_risk_language():
    governed_content = (
        "The organisation cannot sustainably deliver the required "
        "strategic outcome using the current operating capability."
    )

    generated_narrative = (
        "This deficiency poses an existential risk to the organisation."
    )

    result = validate_narrative_language(
        governed_content=governed_content,
        generated_narrative=generated_narrative,
    )

    assert result.valid is False
    assert "existential risk" in result.unsupported_claims


def test_rejects_unsupported_immediate_action_language():
    governed_content = (
        "The organisation cannot sustainably deliver the required "
        "strategic outcome using the current operating capability. "
        "Board approval is required for structural capability intervention."
    )

    generated_narrative = (
        "The Board must take immediate action to rectify this deficiency."
    )

    result = validate_narrative_language(
        governed_content=governed_content,
        generated_narrative=generated_narrative,
    )

    assert result.valid is False
    assert "immediate action" in result.unsupported_claims


def test_allows_immediate_action_when_supported_by_governed_intelligence():
    governed_content = (
        "The identified control failure requires immediate action "
        "to prevent further material exposure."
    )

    generated_narrative = (
        "The Board should take immediate action to address the "
        "identified control failure."
    )

    result = validate_narrative_language(
        governed_content=governed_content,
        generated_narrative=generated_narrative,
    )

    assert result.valid is True
    assert result.unsupported_claims == []


def test_rejects_narrative_that_changes_governed_strategic_position():
    governed_content = (
        "Strategic position: TRANSFORM. "
        "The strategic intent remains valid, but structural capability "
        "is inadequate to deliver it."
    )

    generated_narrative = (
        "The Board should RECONSIDER whether the current strategic "
        "direction remains justified."
    )

    result = validate_narrative_language(
        governed_content=governed_content,
        generated_narrative=generated_narrative,
    )

    assert result.valid is False
    assert "strategic position: RECONSIDER" in result.unsupported_claims


def test_rejects_narrative_that_increases_governed_confidence():
    governed_content = (
        "Strategic position: TRANSFORM. "
        "Confidence: MODERATE. "
        "Evidence indicates a structural capability constraint."
    )

    generated_narrative = (
        "The evidence provides HIGH confidence that the organisation "
        "requires structural transformation."
    )

    result = validate_narrative_language(
        governed_content=governed_content,
        generated_narrative=generated_narrative,
    )

    assert result.valid is False
    assert "confidence: HIGH" in result.unsupported_claims
