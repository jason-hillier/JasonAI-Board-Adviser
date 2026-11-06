"""Regression tests for Macian's cryptographic evidence audit chain."""

from dataclasses import replace

import pytest

from strategic_evidence_audit import EvidenceAuditEvent
from strategic_evidence_audit_hash import (
    calculate_audit_event_hash,
    verify_audit_event_hash,
)
from strategic_evidence_audit_chain import GENESIS_HASH, verify_audit_chain


def make_event(sequence, previous_hash):
    data = {
        "sequence_number": sequence,
        "event_type": "EVIDENCE_REGISTERED",
        "evidence_reference": f"BOARD-{sequence:03d}",
        "actor_identity": "Test Registrar",
        "event_timestamp": "2026-11-06T12:00:00+00:00",
        "evidence_sha256": "a" * 64,
        "previous_event_hash": previous_hash,
    }
    return EvidenceAuditEvent(
        **data,
        event_hash=calculate_audit_event_hash(**data),
    )


@pytest.fixture
def valid_chain():
    first = make_event(1, GENESIS_HASH)
    second = make_event(2, first.event_hash)
    third = make_event(3, second.event_hash)
    return [first, second, third]


def test_valid_chain_passes(valid_chain):
    assert verify_audit_chain(valid_chain)


def test_missing_middle_event_rejected(valid_chain):
    assert not verify_audit_chain([valid_chain[0], valid_chain[2]])


def test_reordered_events_rejected(valid_chain):
    assert not verify_audit_chain(
        [valid_chain[1], valid_chain[0], valid_chain[2]]
    )


def test_modified_event_rejected(valid_chain):
    modified = replace(valid_chain[1], actor_identity="Different Registrar")
    assert not verify_audit_chain(
        [valid_chain[0], modified, valid_chain[2]]
    )


def test_duplicate_sequence_rejected(valid_chain):
    assert not verify_audit_chain(
        [valid_chain[0], valid_chain[1], valid_chain[1]]
    )


def test_modified_fingerprint_rejected(valid_chain):
    modified = replace(valid_chain[1], evidence_sha256="b" * 64)
    assert not verify_audit_chain(
        [valid_chain[0], modified, valid_chain[2]]
    )


def test_deterministic_event_hash():
    event = make_event(1, GENESIS_HASH)
    assert verify_audit_event_hash(event)
    assert event.event_hash == make_event(1, GENESIS_HASH).event_hash


def test_invalid_event_type_rejected():
    assert not verify_audit_event_hash(None)


def test_invalid_chain_input_rejected():
    assert not verify_audit_chain(None)


def test_empty_chain_is_structurally_valid():
    assert verify_audit_chain([])


def test_persistent_storage_rejects_corrupted_audit_history(tmp_path):
    """Registration must fail if an existing audit event is altered."""
    import sqlite3

    from strategic_evidence_storage import EvidenceBaselineStorage
    from strategic_evidence_baseline import EvidenceBaselineRecord
    from strategic_evidence_integrity import EvidenceFingerprint

    database = tmp_path / "evidence.db"
    storage = EvidenceBaselineStorage(str(database))
    storage.initialise()

    def record(number):
        reference = f"BOARD-{number:03d}"
        return EvidenceBaselineRecord(
            evidence_reference=reference,
            fingerprint=EvidenceFingerprint(
                evidence_reference=reference,
                sha256=f"{number:064x}",
                file_size=1024,
            ),
            source_identity="Board Strategy Paper",
            registered_by="Test Registrar",
            registered_at="2026-11-06T12:00:00+00:00",
            source_reference=f"STRATEGY-{number:03d}",
            registration_status="UNVERIFIED",
        )

    storage.register(record(1))
    storage.register(record(2))

    with sqlite3.connect(database) as connection:
        # Simulate privileged interference bypassing SQLite protection.
        connection.execute("DROP TRIGGER prevent_audit_update")
        connection.execute(
            """
            UPDATE evidence_audit_events
            SET actor_identity = ?
            WHERE sequence_number = 1
            """,
            ("Unauthorised Modification",),
        )

    with pytest.raises(ValueError, match="audit chain failed verification"):
        storage.register(record(3))

    with sqlite3.connect(database) as connection:
        baseline_count = connection.execute(
            "SELECT COUNT(*) FROM evidence_baselines"
        ).fetchone()[0]
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM evidence_audit_events"
        ).fetchone()[0]

    assert baseline_count == 2
    assert audit_count == 2


def test_registration_rejects_legacy_evidence_without_audit(tmp_path):
    """Unaudited historical evidence must block new registrations."""
    import sqlite3

    from strategic_evidence_storage import EvidenceBaselineStorage
    from strategic_evidence_baseline import EvidenceBaselineRecord
    from strategic_evidence_integrity import EvidenceFingerprint

    database = tmp_path / "legacy.db"
    storage = EvidenceBaselineStorage(str(database))
    storage.initialise()

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO evidence_baselines (
                evidence_reference, sha256, file_size,
                source_identity, registered_by, registered_at,
                source_reference, registration_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "LEGACY-001", "a" * 64, 1024,
                "Historical Board Paper", "Legacy Registrar",
                "2026-01-01T12:00:00+00:00",
                "HISTORICAL-001", "UNVERIFIED",
            ),
        )

    record = EvidenceBaselineRecord(
        evidence_reference="BOARD-NEW-001",
        fingerprint=EvidenceFingerprint(
            evidence_reference="BOARD-NEW-001",
            sha256="b" * 64,
            file_size=2048,
        ),
        source_identity="New Board Paper",
        registered_by="Test Registrar",
        registered_at="2026-11-06T12:00:00+00:00",
        source_reference="STRATEGY-NEW-001",
        registration_status="UNVERIFIED",
    )

    with pytest.raises(
        ValueError, match="existing baseline lacks matching audit coverage"
    ):
        storage.register(record)

    with sqlite3.connect(database) as connection:
        baselines = connection.execute(
            "SELECT COUNT(*) FROM evidence_baselines"
        ).fetchone()[0]
        events = connection.execute(
            "SELECT COUNT(*) FROM evidence_audit_events"
        ).fetchone()[0]

    assert baselines == 1
    assert events == 0


def test_registration_rejects_orphaned_audit_event(tmp_path):
    """An audit event without its baseline must block registration."""
    import sqlite3

    from strategic_evidence_storage import EvidenceBaselineStorage
    from strategic_evidence_baseline import EvidenceBaselineRecord
    from strategic_evidence_integrity import EvidenceFingerprint

    database = tmp_path / "orphan.db"
    storage = EvidenceBaselineStorage(str(database))
    storage.initialise()

    def record(number):
        reference = f"BOARD-{number:03d}"
        return EvidenceBaselineRecord(
            evidence_reference=reference,
            fingerprint=EvidenceFingerprint(
                evidence_reference=reference,
                sha256=f"{number:064x}",
                file_size=1024,
            ),
            source_identity="Board Strategy Paper",
            registered_by="Test Registrar",
            registered_at="2026-11-06T12:00:00+00:00",
            source_reference=f"STRATEGY-{number:03d}",
            registration_status="UNVERIFIED",
        )

    storage.register(record(1))

    with sqlite3.connect(database) as connection:
        connection.execute(
            "DELETE FROM evidence_baselines WHERE evidence_reference = ?",
            ("BOARD-001",),
        )

    with pytest.raises(
        ValueError, match="audit event lacks matching evidence baseline"
    ):
        storage.register(record(2))

    with sqlite3.connect(database) as connection:
        baseline_count = connection.execute(
            "SELECT COUNT(*) FROM evidence_baselines"
        ).fetchone()[0]

        audit_count = connection.execute(
            "SELECT COUNT(*) FROM evidence_audit_events"
        ).fetchone()[0]

    assert baseline_count == 0
    assert audit_count == 1


def test_audit_triggers_prevent_update_and_delete(tmp_path):
    """Audit events must resist ordinary SQL modification and deletion."""
    import sqlite3

    from strategic_evidence_storage import EvidenceBaselineStorage
    from strategic_evidence_baseline import EvidenceBaselineRecord
    from strategic_evidence_integrity import EvidenceFingerprint

    database = tmp_path / "protected.db"
    storage = EvidenceBaselineStorage(str(database))
    storage.initialise()

    record = EvidenceBaselineRecord(
        evidence_reference="BOARD-PROTECTED-001",
        fingerprint=EvidenceFingerprint(
            evidence_reference="BOARD-PROTECTED-001",
            sha256="a" * 64,
            file_size=1024,
        ),
        source_identity="Board Strategy Paper",
        registered_by="Test Registrar",
        registered_at="2026-11-06T12:00:00+00:00",
        source_reference="STRATEGY-001",
        registration_status="UNVERIFIED",
    )

    storage.register(record)

    with sqlite3.connect(database) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE evidence_audit_events
                SET actor_identity = 'Modified'
                WHERE sequence_number = 1
                """
            )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                DELETE FROM evidence_audit_events
                WHERE sequence_number = 1
                """
            )

        rows = connection.execute(
            """
            SELECT actor_identity
            FROM evidence_audit_events
            """
        ).fetchall()

    assert rows == [("Test Registrar",)]
