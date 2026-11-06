"""Regression tests for Macian evidence baseline registration."""

import pytest

from strategic_evidence_baseline import create_evidence_baseline
from strategic_evidence_integrity import EvidenceFingerprint


def test_valid_baseline_remains_unverified():
    fingerprint = EvidenceFingerprint(
        evidence_reference="BOARD-001",
        sha256="a" * 64,
        file_size=100,
    )

    result = create_evidence_baseline(
        fingerprint=fingerprint,
        source_identity="Board Strategy Office",
        registered_by="Test Registrar",
        source_reference="STRATEGY-001",
    )

    assert result.evidence_reference == "BOARD-001"
    assert result.fingerprint == fingerprint
    assert result.source_identity == "Board Strategy Office"
    assert result.registered_by == "Test Registrar"
    assert result.source_reference == "STRATEGY-001"
    assert result.registered_at
    assert result.registration_status == "UNVERIFIED"


@pytest.mark.parametrize(
    "sha256,file_size",
    [
        ("invalid-hash", 100),
        ("z" * 64, 100),
        ("a" * 64, -1),
        ("a" * 64, True),
    ],
)
def test_invalid_fingerprint_is_rejected(sha256, file_size):
    fingerprint = EvidenceFingerprint(
        evidence_reference="BOARD-001",
        sha256=sha256,
        file_size=file_size,
    )

    with pytest.raises(ValueError):
        create_evidence_baseline(
            fingerprint=fingerprint,
            source_identity="Board Strategy Office",
            registered_by="Test Registrar",
        )


@pytest.mark.parametrize(
    "source_identity,registered_by",
    [
        ("", "Registrar"),
        ("Board Strategy Office", ""),
        (None, "Registrar"),
        ("Board Strategy Office", None),
    ],
)
def test_missing_provenance_metadata_is_rejected(
    source_identity, registered_by
):
    fingerprint = EvidenceFingerprint(
        evidence_reference="BOARD-001",
        sha256="a" * 64,
        file_size=100,
    )

    with pytest.raises(ValueError):
        create_evidence_baseline(
            fingerprint=fingerprint,
            source_identity=source_identity,
            registered_by=registered_by,
        )
