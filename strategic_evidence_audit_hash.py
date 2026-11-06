"""Deterministic SHA-256 hashing for Macian evidence audit events."""

import hashlib
import json

from strategic_evidence_audit import EvidenceAuditEvent


def calculate_audit_event_hash(
    sequence_number: int,
    event_type: str,
    evidence_reference: str,
    actor_identity: str,
    event_timestamp: str,
    evidence_sha256: str,
    previous_event_hash: str,
) -> str:
    """Calculate the canonical SHA-256 hash of an audit event."""

    payload = {
        "sequence_number": sequence_number,
        "event_type": event_type,
        "evidence_reference": evidence_reference,
        "actor_identity": actor_identity,
        "event_timestamp": event_timestamp,
        "evidence_sha256": evidence_sha256,
        "previous_event_hash": previous_event_hash,
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def verify_audit_event_hash(event: EvidenceAuditEvent) -> bool:
    """Check an event against its recorded hash."""

    if not isinstance(event, EvidenceAuditEvent):
        return False

    try:
        calculated = calculate_audit_event_hash(
            sequence_number=event.sequence_number,
            event_type=event.event_type,
            evidence_reference=event.evidence_reference,
            actor_identity=event.actor_identity,
            event_timestamp=event.event_timestamp,
            evidence_sha256=event.evidence_sha256,
            previous_event_hash=event.previous_event_hash,
        )
    except (TypeError, ValueError, OverflowError):
        return False

    return calculated == event.event_hash
