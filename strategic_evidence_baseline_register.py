"""Controlled in-memory register for Macian evidence baselines."""

from datetime import datetime

from strategic_evidence_baseline import EvidenceBaselineRecord
from strategic_evidence_integrity import EvidenceFingerprint


class EvidenceBaselineRegister:
    """Register evidence baselines without allowing silent replacement."""

    def __init__(self):
        self._records = {}

    def register(self, record: EvidenceBaselineRecord) -> None:
        """Validate and register a new evidence baseline."""

        if not isinstance(record, EvidenceBaselineRecord):
            raise ValueError("A valid evidence baseline record is required.")

        reference = record.evidence_reference
        fingerprint = record.fingerprint

        if not isinstance(reference, str) or not reference.strip():
            raise ValueError("A valid evidence reference is required.")

        if not isinstance(fingerprint, EvidenceFingerprint):
            raise ValueError("A valid evidence fingerprint is required.")

        if fingerprint.evidence_reference != reference:
            raise ValueError("Fingerprint evidence reference mismatch.")

        if (
            not isinstance(fingerprint.sha256, str)
            or len(fingerprint.sha256) != 64
            or any(c not in "0123456789abcdef" for c in fingerprint.sha256)
        ):
            raise ValueError("Invalid SHA-256 fingerprint.")

        if type(fingerprint.file_size) is not int or fingerprint.file_size < 0:
            raise ValueError("Invalid evidence file size.")

        for name in ("source_identity", "registered_by"):
            value = getattr(record, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Invalid {name}.")

        if not isinstance(record.source_reference, str):
            raise ValueError("Invalid source reference.")

        if not isinstance(record.registered_at, str):
            raise ValueError("Invalid registration timestamp.")

        try:
            timestamp = datetime.fromisoformat(record.registered_at)
        except ValueError:
            raise ValueError("Invalid registration timestamp.") from None

        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Registration timestamp must include a timezone.")

        if record.registration_status != "UNVERIFIED":
            raise ValueError("Unsupported registration status.")

        if reference in self._records:
            raise ValueError(
                f"Evidence baseline already registered: {reference}"
            )

        self._records[reference] = record

    def get(self, evidence_reference: str) -> EvidenceBaselineRecord | None:
        """Retrieve a registered baseline."""

        if not isinstance(evidence_reference, str):
            return None

        return self._records.get(evidence_reference)

    def count(self) -> int:
        """Return the number of registered evidence baselines."""

        return len(self._records)
