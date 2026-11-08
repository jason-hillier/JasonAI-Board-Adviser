"""Validation engine for Macian independent audit checkpoints."""

import re

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint


def validate_checkpoint(
    checkpoint: EvidenceAuditCheckpoint,
) -> bool:
    """Validate checkpoint metadata without claiming signature verification."""

    if not isinstance(checkpoint, EvidenceAuditCheckpoint):
        return False

    if (
        not isinstance(checkpoint.checkpoint_id, str)
        or not checkpoint.checkpoint_id.strip()
    ):
        return False

    if (
        type(checkpoint.sequence_number) is not int
        or checkpoint.sequence_number < 1
    ):
        return False

    if (
        not isinstance(checkpoint.event_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", checkpoint.event_hash) is None
    ):
        return False

    if (
        not isinstance(checkpoint.checkpoint_timestamp, str)
        or not checkpoint.checkpoint_timestamp.strip()
    ):
        return False

    if (
        not isinstance(checkpoint.checkpoint_authority, str)
        or not checkpoint.checkpoint_authority.strip()
    ):
        return False

    if not isinstance(checkpoint.signature, str):
        return False

    # A checkpoint cannot declare itself verified or trusted.
    # Trust must be established by independent signature verification.
    if checkpoint.verification_status != "UNVERIFIED":
        return False

    return True
