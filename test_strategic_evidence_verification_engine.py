from strategic_evidence_verification import (
    EvidenceVerificationRecord,
    VerificationActivity,
    VerificationOutcome,
)
from strategic_evidence_verification_engine import (
    assess_trusted_evidence_verification,
)


def test_declared_success_does_not_establish_trusted_verification():
    records = [
        EvidenceVerificationRecord(
            evidence_reference="BOARD-EVIDENCE-001",
            activity=activity,
            outcome=VerificationOutcome.PASSED,
            reviewer_identity="Senior Reviewer",
            verification_method="Document review",
            verification_reference="REVIEW-001",
            verification_date="2026-11-06",
        )
        for activity in VerificationActivity
    ]

    result = assess_trusted_evidence_verification(
        "BOARD-EVIDENCE-001", records
    )

    assert result.overall_status == "UNVERIFIED"
    assert len(result.records) == 3
    assert sum(
        "not been independently authenticated" in limitation
        for limitation in result.limitations
    ) == 3
    assert any(
        "No trusted mechanism" in limitation
        for limitation in result.limitations
    )


def test_invalid_record_collection_fails_safely():
    result = assess_trusted_evidence_verification(
        "BOARD-EVIDENCE-001",
        None,
    )

    assert result.overall_status == "UNVERIFIED"
    assert result.records == []
    assert any(
        "must be supplied as a list" in limitation
        for limitation in result.limitations
    )
    assert sum(
        "no verification record supplied" in limitation
        for limitation in result.limitations
    ) == 3


def test_conflicting_verification_records_require_reconciliation():
    records = [
        EvidenceVerificationRecord(
            evidence_reference="BOARD-EVIDENCE-001",
            activity=VerificationActivity.SOURCE_AUTHENTICITY,
            outcome=VerificationOutcome.PASSED,
        ),
        EvidenceVerificationRecord(
            evidence_reference="BOARD-EVIDENCE-001",
            activity=VerificationActivity.SOURCE_AUTHENTICITY,
            outcome=VerificationOutcome.FAILED,
        ),
    ]

    result = assess_trusted_evidence_verification(
        "BOARD-EVIDENCE-001", records
    )

    assert result.overall_status == "UNVERIFIED"
    assert len(result.records) == 2
    assert any(
        "SOURCE_AUTHENTICITY: duplicate verification records"
        in limitation
        for limitation in result.limitations
    )
    assert any(
        "declared PASSED outcome" in limitation
        for limitation in result.limitations
    )
    assert any(
        "reported FAILED outcome" in limitation
        for limitation in result.limitations
    )


def test_missing_reviewer_metadata_is_reported():
    record = EvidenceVerificationRecord(
        evidence_reference="BOARD-EVIDENCE-001",
        activity=VerificationActivity.DOCUMENT_EXISTENCE,
        outcome=VerificationOutcome.PASSED,
    )

    result = assess_trusted_evidence_verification(
        "BOARD-EVIDENCE-001", [record]
    )

    assert result.overall_status == "UNVERIFIED"

    for field in (
        "reviewer_identity",
        "verification_method",
        "verification_reference",
        "verification_date",
    ):
        assert any(
            f"missing or invalid {field}" in limitation
            for limitation in result.limitations
        )


def test_malformed_reviewer_metadata_is_reported():
    record = EvidenceVerificationRecord(
        evidence_reference="BOARD-EVIDENCE-001",
        activity=VerificationActivity.SOURCE_AUTHENTICITY,
        outcome=VerificationOutcome.PASSED,
        reviewer_identity=None,
        verification_method=123,
        verification_reference=[],
        verification_date="",
    )

    result = assess_trusted_evidence_verification(
        "BOARD-EVIDENCE-001", [record]
    )

    assert result.overall_status == "UNVERIFIED"
    assert sum(
        "missing or invalid" in limitation
        for limitation in result.limitations
    ) == 4
