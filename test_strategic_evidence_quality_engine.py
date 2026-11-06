from strategic_evidence_quality_engine import (
    assess_strategic_evidence_quality,
)
from strategic_evidence_quality_criteria import EVIDENCE_QUALITY_CRITERIA


def test_no_information():
    result = assess_strategic_evidence_quality({})

    assert result.overall_status == "INSUFFICIENT_INFORMATION"
    assert len(result.dimensions) == 5
    assert len(result.material_weaknesses) == 5
    assert len(result.board_questions) == 5


def test_complete_information():
    information = {
        criterion.category: {
            field: "Management-supplied information"
            for field in criterion.required_information
        }
        for criterion in EVIDENCE_QUALITY_CRITERIA
    }

    result = assess_strategic_evidence_quality(information)

    assert result.overall_status == "NOT_ASSESSED"
    assert result.material_weaknesses == []
    assert all(
        dimension.status == "NOT_ASSESSED"
        for dimension in result.dimensions
    )


def test_partial_information():
    result = assess_strategic_evidence_quality({
        "CREDIBILITY": {
            "source_identity": "Annual report",
        }
    })

    credibility = next(
        dimension
        for dimension in result.dimensions
        if dimension.category == "CREDIBILITY"
    )

    assert credibility.status == "INSUFFICIENT_INFORMATION"
    assert len(credibility.limitations) == 2
    assert "CREDIBILITY" in result.material_weaknesses


def test_blank_information_is_missing():
    result = assess_strategic_evidence_quality({
        "RELEVANCE": {
            "strategic_claim": "   ",
            "evidence_relationship": "",
        }
    })

    relevance = next(
        dimension
        for dimension in result.dimensions
        if dimension.category == "RELEVANCE"
    )

    assert relevance.status == "INSUFFICIENT_INFORMATION"
    assert len(relevance.limitations) == 2


def test_no_unsubstantiated_quality_rating():
    information = {
        criterion.category: {
            field: "Unverified management assertion"
            for field in criterion.required_information
        }
        for criterion in EVIDENCE_QUALITY_CRITERIA
    }

    result = assess_strategic_evidence_quality(information)

    assert all(
        dimension.status not in ("ADEQUATE", "STRONG")
        for dimension in result.dimensions
    )
    assert all(
        dimension.evidence_references == []
        for dimension in result.dimensions
    )
