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

    def register(self, record) -> None:
        """Validate and persist a baseline without replacing existing records."""

        from strategic_evidence_baseline_register import EvidenceBaselineRegister

        validator = EvidenceBaselineRegister()
        validator.register(record)

        with sqlite3.connect(self.database_path) as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO evidence_baselines (
                        evidence_reference,
                        sha256,
                        file_size,
                        source_identity,
                        registered_by,
                        registered_at,
                        source_reference,
                        registration_status
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
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    "Evidence baseline registration rejected: "
                    "duplicate reference or invalid database constraint."
                ) from error

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
