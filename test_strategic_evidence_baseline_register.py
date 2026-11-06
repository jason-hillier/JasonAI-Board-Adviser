"""Regression tests for Macian's evidence baseline register."""

import pytest

from strategic_evidence_baseline import create_evidence_baseline
from strategic_evidence_baseline_register import EvidenceBaselineRegister
from strategic_evidence_integrity import EvidenceFingerprint


def make_baseline(reference="BOARD-001", sha256=None):
    fingerprint = EvidenceFingerprint(
        evidence_reference=reference,
        sha256=sha256 or "a" * 64,
        file_size=100,
    )
    return create_evidence_baseline(
        fingerprint=fingerprint,
        source_identity="Board Strategy Office",
        registered_by="Test Registrar",
    )


def test_register_and_retrieve_baseline():
    register = EvidenceBaselineRegister()
    baseline = make_baseline()

    register.register(baseline)

    assert register.count() == 1
    assert register.get("BOARD-001") == baseline


def test_duplicate_registration_rejected():
    register = EvidenceBaselineRegister()
    original = make_baseline()
    replacement = make_baseline(sha256="b" * 64)

    register.register(original)

    with pytest.raises(ValueError):
        register.register(replacement)

    assert register.count() == 1
    assert register.get("BOARD-001") == original


def test_invalid_record_rejected():
    register = EvidenceBaselineRegister()

    with pytest.raises(ValueError):
        register.register(None)

    assert register.count() == 0


def test_unknown_reference_returns_none():
    register = EvidenceBaselineRegister()

    assert register.get("UNKNOWN-001") is None


def test_multiple_unique_baselines():
    register = EvidenceBaselineRegister()

    register.register(make_baseline("BOARD-001"))
    register.register(make_baseline("BOARD-002"))

    assert register.count() == 2
    assert register.get("BOARD-001") is not None
    assert register.get("BOARD-002") is not None


@pytest.mark.parametrize(
    "changes",
    [
        {"evidence_reference": "BOARD-002"},
        {"source_identity": ""},
        {"registered_by": None},
        {"source_reference": None},
        {"registered_at": "not-a-date"},
        {"registered_at": "2026-11-06T12:00:00"},
        {"registration_status": "VERIFIED"},
        {"fingerprint": None},
        {
            "fingerprint": EvidenceFingerprint(
                evidence_reference="BOARD-001",
                sha256="invalid",
                file_size=100,
            )
        },
        {
            "fingerprint": EvidenceFingerprint(
                evidence_reference="BOARD-001",
                sha256="a" * 64,
                file_size=-1,
            )
        },
    ],
)
def test_malformed_baseline_records_are_rejected(changes):
    from dataclasses import replace

    register = EvidenceBaselineRegister()
    valid_record = make_baseline()
    malformed_record = replace(valid_record, **changes)

    with pytest.raises(ValueError):
        register.register(malformed_record)

    assert register.count() == 0
