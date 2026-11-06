"""Regression tests for Macian's persistent evidence storage."""

import sqlite3

import pytest

from strategic_evidence_baseline import create_evidence_baseline
from strategic_evidence_integrity import EvidenceFingerprint
from strategic_evidence_storage import EvidenceBaselineStorage


@pytest.fixture
def storage(tmp_path):
    repository = EvidenceBaselineStorage(str(tmp_path / "evidence.db"))
    repository.initialise()
    return repository


def make_baseline(reference="BOARD-001", sha256=None):
    return create_evidence_baseline(
        fingerprint=EvidenceFingerprint(
            evidence_reference=reference,
            sha256=sha256 or "a" * 64,
            file_size=100,
        ),
        source_identity="Board Strategy Office",
        registered_by="Test Registrar",
        source_reference="STRATEGY-001",
    )


def test_database_initialisation_is_repeatable(storage):
    storage.initialise()
    assert storage.get("UNKNOWN-001") is None


def test_baseline_persists_across_connections(storage):
    original = make_baseline()
    storage.register(original)

    reopened = EvidenceBaselineStorage(str(storage.database_path))

    assert reopened.get("BOARD-001") == original


def test_duplicate_registration_preserves_original(storage):
    original = make_baseline()
    replacement = make_baseline(sha256="b" * 64)

    storage.register(original)

    with pytest.raises(ValueError):
        storage.register(replacement)

    assert storage.get("BOARD-001") == original


def test_invalid_record_rejected(storage):
    with pytest.raises(ValueError):
        storage.register(None)

    assert storage.get("BOARD-001") is None


def test_multiple_baselines(storage):
    storage.register(make_baseline("BOARD-001"))
    storage.register(make_baseline("BOARD-002"))

    assert storage.get("BOARD-001") is not None
    assert storage.get("BOARD-002") is not None


def test_unknown_reference_returns_none(storage):
    assert storage.get("UNKNOWN-001") is None


def test_invalid_lookup_reference_rejected(storage):
    with pytest.raises(ValueError):
        storage.get("")


def test_database_enforces_unique_reference(storage):
    storage.register(make_baseline())

    with sqlite3.connect(storage.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO evidence_baselines (
                    evidence_reference, sha256, file_size,
                    source_identity, registered_by, registered_at,
                    source_reference, registration_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "BOARD-001", "b" * 64, 200,
                    "Different Source", "Other Registrar",
                    "2026-11-06T12:00:00+00:00",
                    "", "UNVERIFIED",
                ),
            )

    assert storage.get("BOARD-001").fingerprint.sha256 == "a" * 64
