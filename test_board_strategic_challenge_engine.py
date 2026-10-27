from board_strategic_challenge_engine import assess_board_strategic_challenge


def test_missing_evidence():
    result = assess_board_strategic_challenge(
        "Modernise the platform", "", ["Replace the platform"]
    )
    assert result.overall_assessment == "CHALLENGE_REQUIRED"
    assert any(f.category == "EVIDENCE" for f in result.findings)


def test_missing_alternatives():
    result = assess_board_strategic_challenge(
        "Modernise the platform", "Approved business case", []
    )
    assert result.overall_assessment == "CHALLENGE_REQUIRED"
    assert any(
        f.category == "STRATEGIC_ALTERNATIVES"
        for f in result.findings
    )


def test_complete_submission():
    result = assess_board_strategic_challenge(
        "Modernise the platform",
        "Approved business case",
        ["Replace the platform"],
    )
    assert result.overall_assessment == "NO_GAPS_IDENTIFIED"
    assert len(result.findings) == 0


def test_missing_recommendation():
    result = assess_board_strategic_challenge(
        "", "Supporting evidence", ["Modernise the platform"]
    )
    assert result.overall_assessment == "CHALLENGE_REQUIRED"
    assert any(
        f.category == "STRATEGIC_RATIONALE"
        for f in result.findings
    )
