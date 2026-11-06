"""Evidence baseline records for Macian's governance framework."""

from dataclasses import dataclass
from datetime import datetime, timezone

from strategic_evidence_integrity import EvidenceFingerprint


@dataclass(frozen=True)
class EvidenceBaselineRecord:
    evidence_reference: str
    fingerprint: EvidenceFingerprint
    source_identity: str
    registered_by: str
    registered_at: str
    source_reference: str = ""
    registration_status: str = "UNVERIFIED"


def create_evidence_baseline(
    fingerprint: EvidenceFingerprint,
    source_identity: str,
    registered_by: str,
    source_reference: str = "",
) -> EvidenceBaselineRecord:
    """Create a baseline record without claiming independent verification."""

    if not isinstance(fingerprint, EvidenceFingerprint):
        raise ValueError("A valid evidence fingerprint is required.")

    if not isinstance(fingerprint.evidence_reference, str) or not fingerprint.evidence_reference.strip():
        raise ValueError("A valid evidence reference is required.")

    if (
        not isinstance(fingerprint.sha256, str)
        or len(fingerprint.sha256) != 64
        or any(c not in "0123456789abcdef" for c in fingerprint.sha256)
    ):
        raise ValueError("A valid SHA-256 fingerprint is required.")

    if type(fingerprint.file_size) is not int or fingerprint.file_size < 0:
        raise ValueError("A valid evidence file size is required.")

    for name, value in (
        ("source_identity", source_identity),
        ("registered_by", registered_by),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"A valid {name} is required.")

    if not isinstance(source_reference, str):
        raise ValueError("Source reference must be a string.")

    return EvidenceBaselineRecord(
        evidence_reference=fingerprint.evidence_reference,
        fingerprint=fingerprint,
        source_identity=source_identity,
        registered_by=registered_by,
        registered_at=datetime.now(timezone.utc).isoformat(),
        source_reference=source_reference,
        registration_status="UNVERIFIED",
    )
