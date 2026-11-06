from strategic_evidence_credibility import (
    CredibilityVerificationStatus,
    EvidenceCredibilityRecord,
)
from strategic_evidence_credibility_engine import (
    evaluate_evidence_credibility,
)


def test_missing_evidence_identifies_all_gaps():
    result = evaluate_evidence_credibility(EvidenceCredibilityRecord())

    assert result.status == "UNVERIFIED"
    assert len(result.documentation_gaps) == 4
    assert len(result.verification_gaps) == 2


def test_documented_evidence_is_not_automatically_verified():
    record = EvidenceCredibilityRecord(
        source_identity="Independent research organisation",
        source_authority="Published research methodology",
        source_reference="REPORT-001",
        corroborating_references=["REPORT-002"],
        verification_status=CredibilityVerificationStatus.DOCUMENTED,
    )

    result = evaluate_evidence_credibility(record)

    assert result.status == "UNVERIFIED"
    assert result.documentation_gaps == []
    assert "verified_by" in result.verification_gaps


def test_declared_verification_is_not_accepted_as_proof():
    record = EvidenceCredibilityRecord(
        source_identity="External auditor",
        source_authority="Audit report",
        source_reference="AUDIT-001",
        corroborating_references=["AUDIT-002"],
        verification_status=CredibilityVerificationStatus.VERIFIED,
        verified_by="Reviewer",
        verification_reference="REVIEW-001",
    )

    result = evaluate_evidence_credibility(record)

    assert result.status == "UNVERIFIED"
    assert any(
        "not been independently authenticated" in gap
        for gap in result.verification_gaps
    )
    assert result.documentation_gaps == []


def test_malformed_verification_fields_are_reported():
    record = EvidenceCredibilityRecord(
        verified_by=None,
        verification_reference=123,
    )

    result = evaluate_evidence_credibility(record)

    assert result.status == "UNVERIFIED"
    assert "verified_by" in result.verification_gaps
    assert "verification_reference" in result.verification_gaps


def test_malformed_corroboration_is_reported():
    record = EvidenceCredibilityRecord(
        source_identity="Research organisation",
        source_authority="Published methodology",
        source_reference="REPORT-001",
        corroborating_references=None,
    )

    result = evaluate_evidence_credibility(record)

    assert result.status == "UNVERIFIED"
    assert "corroborating_references" in result.documentation_gaps
