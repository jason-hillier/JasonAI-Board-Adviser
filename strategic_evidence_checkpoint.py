"""Independent audit checkpoint records for Macian."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceAuditCheckpoint:
    checkpoint_id: str
    sequence_number: int
    event_hash: str
    checkpoint_timestamp: str
    checkpoint_authority: str
    signature: str = ""
    signing_key_id: str = ""
    verification_status: str = "UNVERIFIED"
