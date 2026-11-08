"""Trusted signature verification for Macian audit checkpoints."""

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_engine import validate_checkpoint
from strategic_evidence_checkpoint_signing import verify_checkpoint_signature
from strategic_evidence_trusted_keys import TrustedKeyRegistry


def verify_trusted_checkpoint(
    checkpoint: EvidenceAuditCheckpoint,
    registry: TrustedKeyRegistry,
) -> bool:
    """Verify metadata, signing authority and Ed25519 signature."""

    if not isinstance(registry, TrustedKeyRegistry):
        return False

    if not validate_checkpoint(checkpoint):
        return False

    if not isinstance(checkpoint.signing_key_id, str):
        return False

    record = registry.get_trusted_key(checkpoint.signing_key_id)

    if record is None:
        return False

    if checkpoint.checkpoint_authority != record.authority:
        return False

    return verify_checkpoint_signature(
        checkpoint,
        record.public_key,
        expected_key_id=record.key_id,
    )


def verify_checkpoint_key_validity(
    checkpoint: EvidenceAuditCheckpoint,
    registry: TrustedKeyRegistry,
) -> bool:
    """Check key authorisation against the checkpoint's claimed timestamp.

    This is a policy check, not independent proof of signing time.
    """
    from strategic_evidence_key_time import parse_key_timestamp

    if not verify_trusted_checkpoint(checkpoint, registry):
        return False

    try:
        record = registry.get_trusted_key(checkpoint.signing_key_id)
        if record is None:
            return False

        checkpoint_time = parse_key_timestamp(
            checkpoint.checkpoint_timestamp
        )

        if record.valid_from is None:
            return False

        activation_time = parse_key_timestamp(record.valid_from)

        if checkpoint_time < activation_time:
            return False

        if record.valid_until is not None:
            expiry_time = parse_key_timestamp(record.valid_until)

            if checkpoint_time >= expiry_time:
                return False

        return True

    except (ValueError, TypeError):
        return False
