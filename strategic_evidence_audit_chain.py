"""Hash-linked audit chain verification for Macian."""

from strategic_evidence_audit import EvidenceAuditEvent
from strategic_evidence_audit_hash import verify_audit_event_hash


GENESIS_HASH = "0" * 64


def verify_audit_chain(events: list[EvidenceAuditEvent]) -> bool:
    """Verify event hashes, sequence continuity and hash links."""

    if not isinstance(events, list):
        return False

    expected_sequence = 1
    expected_previous_hash = GENESIS_HASH

    for event in events:
        if not isinstance(event, EvidenceAuditEvent):
            return False

        if type(event.sequence_number) is not int:
            return False

        if event.sequence_number != expected_sequence:
            return False

        if event.previous_event_hash != expected_previous_hash:
            return False

        if not verify_audit_event_hash(event):
            return False

        expected_previous_hash = event.event_hash
        expected_sequence += 1

    return True
