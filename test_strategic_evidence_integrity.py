"""Regression tests for strategic evidence integrity."""

import hashlib

from strategic_evidence_integrity import (
    EvidenceFingerprint,
    fingerprint_evidence,
    verify_evidence_integrity,
)


def test_fingerprint_generation(tmp_path):
    path = tmp_path / "evidence.txt"
    content = b"Original Board evidence"
    path.write_bytes(content)

    result = fingerprint_evidence("BOARD-001", str(path))

    assert result.evidence_reference == "BOARD-001"
    assert result.sha256 == hashlib.sha256(content).hexdigest()
    assert result.file_size == len(content)


def test_unchanged_evidence_matches(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_text("Original Board evidence")

    baseline = fingerprint_evidence("BOARD-001", str(path))
    result = verify_evidence_integrity(baseline, str(path))

    assert result.status == "MATCH"


def test_modified_evidence_is_detected(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_text("Original Board evidence")

    baseline = fingerprint_evidence("BOARD-001", str(path))
    path.write_text("Modified Board evidence")

    result = verify_evidence_integrity(baseline, str(path))

    assert result.status == "MISMATCH"


def test_missing_evidence_is_unverified(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_text("Original Board evidence")

    baseline = fingerprint_evidence("BOARD-001", str(path))
    path.unlink()

    result = verify_evidence_integrity(baseline, str(path))

    assert result.status == "UNVERIFIED"


def test_invalid_baseline_is_unverified(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_text("Original Board evidence")

    baseline = EvidenceFingerprint(
        evidence_reference="BOARD-001",
        sha256="invalid-hash",
        file_size=23,
    )

    result = verify_evidence_integrity(baseline, str(path))

    assert result.status == "UNVERIFIED"
