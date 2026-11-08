"""Ed25519 signing and verification for Macian audit checkpoints."""

import base64
import hashlib
import json

from dataclasses import replace

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint


def generate_key_pair():
    """Generate an Ed25519 private/public key pair."""
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def get_signing_key_id(public_key: Ed25519PublicKey) -> str:
    """Calculate a stable identifier for a public signing key."""
    if not isinstance(public_key, Ed25519PublicKey):
        raise ValueError("A valid Ed25519 public key is required.")

    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return hashlib.sha256(raw_key).hexdigest()


def canonical_checkpoint_payload(
    checkpoint: EvidenceAuditCheckpoint,
    signing_key_id: str,
) -> bytes:
    """Produce deterministic bytes for checkpoint signing."""
    payload = {
        "checkpoint_id": checkpoint.checkpoint_id,
        "sequence_number": checkpoint.sequence_number,
        "event_hash": checkpoint.event_hash,
        "checkpoint_timestamp": checkpoint.checkpoint_timestamp,
        "checkpoint_authority": checkpoint.checkpoint_authority,
        "signing_key_id": signing_key_id,
    }

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sign_checkpoint(
    checkpoint: EvidenceAuditCheckpoint,
    private_key: Ed25519PrivateKey,
) -> EvidenceAuditCheckpoint:
    """Sign checkpoint metadata without declaring it independently trusted."""
    if not isinstance(checkpoint, EvidenceAuditCheckpoint):
        raise ValueError("A valid checkpoint is required.")

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("A valid Ed25519 private key is required.")

    if checkpoint.verification_status != "UNVERIFIED":
        raise ValueError("Only unverified checkpoints can be signed.")

    public_key = private_key.public_key()
    key_id = get_signing_key_id(public_key)

    payload = canonical_checkpoint_payload(checkpoint, key_id)
    signature = private_key.sign(payload)

    return replace(
        checkpoint,
        signature=base64.b64encode(signature).decode("ascii"),
        signing_key_id=key_id,
        verification_status="UNVERIFIED",
    )


def verify_checkpoint_signature(
    checkpoint: EvidenceAuditCheckpoint,
    trusted_public_key: Ed25519PublicKey,
    expected_key_id: str | None = None,
) -> bool:
    """Verify a checkpoint signature against a supplied trusted public key."""
    if not isinstance(checkpoint, EvidenceAuditCheckpoint):
        return False

    if not isinstance(trusted_public_key, Ed25519PublicKey):
        return False

    try:
        actual_key_id = get_signing_key_id(trusted_public_key)

        if checkpoint.signing_key_id != actual_key_id:
            return False

        if expected_key_id is not None and expected_key_id != actual_key_id:
            return False

        signature = base64.b64decode(
            checkpoint.signature,
            validate=True,
        )

        payload = canonical_checkpoint_payload(
            checkpoint,
            actual_key_id,
        )

        trusted_public_key.verify(signature, payload)

        return True

    except (InvalidSignature, ValueError, TypeError, AttributeError):
        return False
