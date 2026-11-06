"""Audit event model for Macian's evidence governance framework."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class EvidenceAuditEvent:
    """A recorded evidence governance event."""

    sequence_number: int
    event_type: str
    evidence_reference: str
    actor_identity: str
    event_timestamp: str
    evidence_sha256: str
    previous_event_hash: str
    event_hash: str


def create_audit_timestamp() -> str:
    """Generate a timezone-aware UTC audit timestamp."""

    return datetime.now(timezone.utc).isoformat()
