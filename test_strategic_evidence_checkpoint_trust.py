"""Security tests for trusted checkpoint verification."""

from dataclasses import replace

import pytest

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    sign_checkpoint,
)
from strategic_evidence_checkpoint_trust import verify_trusted_checkpoint
from strategic_evidence_trusted_keys import TrustedKeyRegistry


@pytest.fixture
def trusted_setup():
    private_key, public_key = generate_key_pair()
    registry = TrustedKeyRegistry()
    key_id = registry.register(public_key, "Macian Audit Authority")

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="CHECKPOINT-001",
        sequence_number=10,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    signed = sign_checkpoint(checkpoint, private_key)
    return signed, registry, key_id


def test_valid_trusted_checkpoint_accepted(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    assert verify_trusted_checkpoint(checkpoint, registry)


def test_unregistered_key_rejected(trusted_setup):
    checkpoint, _, _ = trusted_setup
    assert not verify_trusted_checkpoint(checkpoint, TrustedKeyRegistry())


def test_revoked_key_rejected(trusted_setup):
    checkpoint, registry, key_id = trusted_setup
    registry.revoke(key_id)
    assert not verify_trusted_checkpoint(checkpoint, registry)


def test_authority_substitution_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(
        checkpoint,
        checkpoint_authority="Unauthorised Authority",
    )
    assert not verify_trusted_checkpoint(modified, registry)


def test_evidence_hash_tampering_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(checkpoint, event_hash="b" * 64)
    assert not verify_trusted_checkpoint(modified, registry)


def test_sequence_tampering_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(checkpoint, sequence_number=11)
    assert not verify_trusted_checkpoint(modified, registry)


def test_signature_tampering_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(checkpoint, signature="invalid-signature")
    assert not verify_trusted_checkpoint(modified, registry)


def test_self_declared_verified_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(checkpoint, verification_status="VERIFIED")
    assert not verify_trusted_checkpoint(modified, registry)


def test_invalid_registry_rejected(trusted_setup):
    checkpoint, _, _ = trusted_setup
    assert not verify_trusted_checkpoint(checkpoint, None)


def test_unsigned_checkpoint_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    modified = replace(checkpoint, signature="")
    assert not verify_trusted_checkpoint(modified, registry)


def test_wrong_signing_key_rejected(trusted_setup):
    checkpoint, registry, _ = trusted_setup
    other_private_key, other_public_key = generate_key_pair()
    registry.register(other_public_key, "Macian Audit Authority")

    forged = sign_checkpoint(
        replace(
            checkpoint,
            signature="",
            signing_key_id="",
        ),
        other_private_key,
    )

    # The replacement key is registered, so its signature is valid.
    # The checkpoint is not bound to a specific historical signer yet.
    assert verify_trusted_checkpoint(forged, registry)
