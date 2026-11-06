"""Cryptographic integrity controls for strategic evidence."""

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvidenceFingerprint:
    evidence_reference: str
    sha256: str
    file_size: int


def fingerprint_evidence(
    evidence_reference: str,
    file_path: str,
) -> EvidenceFingerprint:
    """Calculate a SHA-256 fingerprint of an evidence file."""

    if not isinstance(evidence_reference, str) or not evidence_reference.strip():
        raise ValueError("A valid evidence reference is required.")

    path = Path(file_path)

    if not path.is_file():
        raise ValueError("Evidence file does not exist.")

    digest = hashlib.sha256()
    file_size = 0

    with path.open("rb") as evidence_file:
        for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
            digest.update(chunk)
            file_size += len(chunk)

    return EvidenceFingerprint(
        evidence_reference=evidence_reference,
        sha256=digest.hexdigest(),
        file_size=file_size,
    )


@dataclass(frozen=True)
class EvidenceIntegrityAssessment:
    evidence_reference: str
    status: str
    rationale: str


def verify_evidence_integrity(
    expected: EvidenceFingerprint,
    file_path: str,
) -> EvidenceIntegrityAssessment:
    """Compare a document with its previously recorded fingerprint."""

    if not isinstance(expected, EvidenceFingerprint):
        return EvidenceIntegrityAssessment(
            evidence_reference="",
            status="UNVERIFIED",
            rationale="Invalid reference fingerprint.",
        )

    if (
        not isinstance(expected.evidence_reference, str)
        or not expected.evidence_reference.strip()
        or not isinstance(expected.sha256, str)
        or len(expected.sha256) != 64
        or any(c not in "0123456789abcdef" for c in expected.sha256)
        or type(expected.file_size) is not int
        or expected.file_size < 0
    ):
        return EvidenceIntegrityAssessment(
            evidence_reference=str(expected.evidence_reference),
            status="UNVERIFIED",
            rationale="Invalid fingerprint metadata.",
        )

    try:
        actual = fingerprint_evidence(
            expected.evidence_reference,
            file_path,
        )
    except (OSError, ValueError, TypeError):
        return EvidenceIntegrityAssessment(
            evidence_reference=expected.evidence_reference,
            status="UNVERIFIED",
            rationale="Evidence file could not be read reliably.",
        )

    if (
        actual.sha256 == expected.sha256
        and actual.file_size == expected.file_size
    ):
        return EvidenceIntegrityAssessment(
            evidence_reference=expected.evidence_reference,
            status="MATCH",
            rationale="Document matches the recorded fingerprint.",
        )

    return EvidenceIntegrityAssessment(
        evidence_reference=expected.evidence_reference,
        status="MISMATCH",
        rationale="Document differs from the recorded fingerprint.",
    )
