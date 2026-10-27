from strategic_assurance_engine import assess_strategic_assurance
from strategic_assurance_status import AssuranceCategory


def test_no_evidence():
    result = assess_strategic_assurance({})

    assert result.overall_status == "MISSING_EVIDENCE"
    assert len(result.critical_gaps) == 5
    assert len(result.board_questions) == 5
    assert all(
        dimension.status == "MISSING_EVIDENCE"
        for dimension in result.dimensions
    )


def test_all_evidence_supplied():
    evidence = {
        category.value: ["Supporting management document"]
        for category in AssuranceCategory
    }

    result = assess_strategic_assurance(evidence)

    assert result.overall_status == "UNVERIFIED"
    assert result.critical_gaps == []
    assert all(
        dimension.status == "UNVERIFIED"
        for dimension in result.dimensions
    )


def test_mixed_evidence():
    result = assess_strategic_assurance({
        "STRATEGIC_RATIONALE": ["Approved strategy paper"],
        "INVESTMENT_CASE": ["Financial forecast"],
    })

    statuses = {
        dimension.category: dimension.status
        for dimension in result.dimensions
    }

    assert statuses["STRATEGIC_RATIONALE"] == "UNVERIFIED"
    assert statuses["INVESTMENT_CASE"] == "UNVERIFIED"
    assert statuses["STRATEGIC_ALTERNATIVES"] == "MISSING_EVIDENCE"
    assert len(result.critical_gaps) == 3


def test_blank_evidence_is_missing():
    result = assess_strategic_assurance({
        "STRATEGIC_RATIONALE": ["", "   "],
    })

    rationale = next(
        dimension
        for dimension in result.dimensions
        if dimension.category == "STRATEGIC_RATIONALE"
    )

    assert rationale.status == "MISSING_EVIDENCE"
    assert rationale.evidence_references == []


def test_assessment_structure():
    result = assess_strategic_assurance({})

    assert len(result.dimensions) == 5
    assert len({d.category for d in result.dimensions}) == 5
    assert all(d.assurance_requirements for d in result.dimensions)
    assert all(d.rationale for d in result.dimensions)
