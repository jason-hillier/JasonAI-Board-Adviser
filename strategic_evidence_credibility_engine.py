from dataclasses import dataclass, field

from strategic_evidence_credibility import (
    CredibilityVerificationStatus,
    EvidenceCredibilityRecord,
)


@dataclass
class CredibilityEvaluation:
    status: str = "UNVERIFIED"
    documentation_gaps: list[str] = field(default_factory=list)
    verification_gaps: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


def evaluate_evidence_credibility(
    record: EvidenceCredibilityRecord,
) -> CredibilityEvaluation:
    """Assess documentation gaps without certifying source credibility."""

    documentation_gaps = []

    for attribute in (
        "source_identity",
        "source_authority",
        "source_reference",
    ):
        value = getattr(record, attribute)
        if not isinstance(value, str) or not value.strip():
            documentation_gaps.append(attribute)

    references = record.corroborating_references

    if (
        not isinstance(references, list)
        or not any(
            isinstance(ref, str) and ref.strip()
            for ref in references
        )
    ):
        documentation_gaps.append("corroborating_references")

    verification_gaps = []

    if (
        not isinstance(record.verified_by, str)
        or not record.verified_by.strip()
    ):
        verification_gaps.append("verified_by")

    if (
        not isinstance(record.verification_reference, str)
        or not record.verification_reference.strip()
    ):
        verification_gaps.append("verification_reference")

    if record.verification_status == CredibilityVerificationStatus.VERIFIED:
        verification_gaps.append(
            "Declared verification has not been independently authenticated"
        )

    return CredibilityEvaluation(
        status="UNVERIFIED",
        documentation_gaps=documentation_gaps,
        verification_gaps=verification_gaps,
        limitations=[
            "Source authority has not been independently established.",
            "Corroborating references have not been independently examined.",
            "No positive evidence credibility rating has been awarded.",
        ],
    )
