"""SQLite persistence for Macian evidence baselines."""

import sqlite3
from pathlib import Path


class EvidenceBaselineStorage:
    """Persistent storage for evidence baseline records."""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)

    def initialise(self) -> None:
        """Create the evidence baseline table if it does not exist."""

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS evidence_baselines (
                    evidence_reference TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    source_identity TEXT NOT NULL,
                    registered_by TEXT NOT NULL,
                    registered_at TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    registration_status TEXT NOT NULL
                        CHECK (registration_status = 'UNVERIFIED')
                )
            """)
            connection.commit()

        self.initialise_audit_trail()
        self.protect_audit_trail()

    def register(self, record) -> None:
        """Register evidence through the mandatory atomic audit transaction."""
        self.register_with_audit(record)

    def get(self, evidence_reference: str):
        """Retrieve a persisted evidence baseline by reference."""

        from strategic_evidence_baseline import EvidenceBaselineRecord
        from strategic_evidence_integrity import EvidenceFingerprint

        if not isinstance(evidence_reference, str) or not evidence_reference.strip():
            raise ValueError("A valid evidence reference is required.")

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT evidence_reference, sha256, file_size,
                       source_identity, registered_by, registered_at,
                       source_reference, registration_status
                FROM evidence_baselines
                WHERE evidence_reference = ?
                """,
                (evidence_reference,),
            ).fetchone()

        if row is None:
            return None

        return EvidenceBaselineRecord(
            evidence_reference=row[0],
            fingerprint=EvidenceFingerprint(
                evidence_reference=row[0],
                sha256=row[1],
                file_size=row[2],
            ),
            source_identity=row[3],
            registered_by=row[4],
            registered_at=row[5],
            source_reference=row[6],
            registration_status=row[7],
        )

    def protect_audit_trail(self) -> None:
        """Reject ordinary SQL updates and deletes of audit events."""

        with sqlite3.connect(self.database_path) as connection:
            connection.executescript("""
                CREATE TRIGGER IF NOT EXISTS prevent_audit_update
                BEFORE UPDATE ON evidence_audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'Audit events cannot be modified');
                END;

                CREATE TRIGGER IF NOT EXISTS prevent_audit_delete
                BEFORE DELETE ON evidence_audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'Audit events cannot be deleted');
                END;
            """)

    def initialise_audit_trail(self) -> None:
        """Create the persistent evidence audit event table."""

        with sqlite3.connect(self.database_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS evidence_audit_events (
                    sequence_number INTEGER PRIMARY KEY
                        CHECK (sequence_number > 0),
                    event_type TEXT NOT NULL,
                    evidence_reference TEXT NOT NULL,
                    actor_identity TEXT NOT NULL,
                    event_timestamp TEXT NOT NULL,
                    evidence_sha256 TEXT NOT NULL,
                    previous_event_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                )
            """)

    def register_with_audit(self, record) -> None:
        """Atomically register evidence and its hash-linked audit event."""

        from strategic_evidence_baseline_register import EvidenceBaselineRegister
        from strategic_evidence_audit import create_audit_timestamp
        from strategic_evidence_audit_chain import GENESIS_HASH
        from strategic_evidence_audit_hash import calculate_audit_event_hash

        validator = EvidenceBaselineRegister()
        validator.register(record)

        with sqlite3.connect(self.database_path, timeout=30) as connection:
            connection.execute("BEGIN IMMEDIATE")

            try:
                from strategic_evidence_audit import EvidenceAuditEvent
                from strategic_evidence_audit_chain import verify_audit_chain

                rows = connection.execute(
                    """
                    SELECT sequence_number, event_type, evidence_reference,
                           actor_identity, event_timestamp, evidence_sha256,
                           previous_event_hash, event_hash
                    FROM evidence_audit_events
                    ORDER BY sequence_number
                    """
                ).fetchall()

                events = [EvidenceAuditEvent(*row) for row in rows]

                if not verify_audit_chain(events):
                    raise ValueError(
                        "Evidence registration rejected: "
                        "existing audit chain failed verification."
                    )

                missing_coverage = connection.execute(
                    """
                    SELECT b.evidence_reference
                    FROM evidence_baselines AS b
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM evidence_audit_events AS a
                        WHERE a.evidence_reference = b.evidence_reference
                          AND a.evidence_sha256 = b.sha256
                          AND a.event_type = 'EVIDENCE_REGISTERED'
                    )
                    LIMIT 1
                    """
                ).fetchone()

                if missing_coverage is not None:
                    raise ValueError(
                        "Evidence registration rejected: "
                        "existing baseline lacks matching audit coverage."
                    )

                orphaned_event = connection.execute(
                    """
                    SELECT a.evidence_reference
                    FROM evidence_audit_events AS a
                    WHERE a.event_type = 'EVIDENCE_REGISTERED'
                      AND NOT EXISTS (
                          SELECT 1
                          FROM evidence_baselines AS b
                          WHERE b.evidence_reference = a.evidence_reference
                            AND b.sha256 = a.evidence_sha256
                      )
                    LIMIT 1
                    """
                ).fetchone()

                if orphaned_event is not None:
                    raise ValueError(
                        "Evidence registration rejected: "
                        "audit event lacks matching evidence baseline."
                    )

                previous = events[-1] if events else None
                sequence = previous.sequence_number + 1 if previous else 1
                previous_hash = previous.event_hash if previous else GENESIS_HASH

                connection.execute(
                    """
                    INSERT INTO evidence_baselines (
                        evidence_reference, sha256, file_size,
                        source_identity, registered_by, registered_at,
                        source_reference, registration_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.evidence_reference,
                        record.fingerprint.sha256,
                        record.fingerprint.file_size,
                        record.source_identity,
                        record.registered_by,
                        record.registered_at,
                        record.source_reference,
                        record.registration_status,
                    ),
                )

                timestamp = create_audit_timestamp()

                event_hash = calculate_audit_event_hash(
                    sequence_number=sequence,
                    event_type="EVIDENCE_REGISTERED",
                    evidence_reference=record.evidence_reference,
                    actor_identity=record.registered_by,
                    event_timestamp=timestamp,
                    evidence_sha256=record.fingerprint.sha256,
                    previous_event_hash=previous_hash,
                )

                connection.execute(
                    """
                    INSERT INTO evidence_audit_events (
                        sequence_number, event_type, evidence_reference,
                        actor_identity, event_timestamp, evidence_sha256,
                        previous_event_hash, event_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sequence, "EVIDENCE_REGISTERED",
                        record.evidence_reference, record.registered_by,
                        timestamp, record.fingerprint.sha256,
                        previous_hash, event_hash,
                    ),
                )

            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "Atomic evidence registration rejected."
                ) from error
