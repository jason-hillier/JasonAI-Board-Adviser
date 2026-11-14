"""Adversarial tests for Macian authority rotation."""

import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from strategic_evidence_authority_rotation import (
    ROTATION_DOMAIN,
    verify_authority_rotation,
)


def fingerprint(key):
    return hashlib.sha256(
        key.public_key().public_bytes_raw()
    ).hexdigest()


def signed_rotation(existing_key, proposed_key):
    record = {
        "format": "macian.authority-rotation",
        "version": 1,
        "rotation_id": "ROT-001",
        "existing_fingerprint": fingerprint(existing_key),
        "proposed_fingerprint": fingerprint(proposed_key),
        "requested_by": "Security Operations",
        "approved_by": "Independent Authority",
        "approved_at": "2026-11-14T12:00:00Z",
        "reason": "Scheduled authority replacement",
    }

    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    record["signature"] = existing_key.sign(
        ROTATION_DOMAIN + payload
    )
    return record


def setup_rotation():
    existing = Ed25519PrivateKey.generate()
    proposed = Ed25519PrivateKey.generate()
    record = signed_rotation(existing, proposed)
    return existing, proposed, record


def verify(record, existing, trusted=None):
    return verify_authority_rotation(
        record,
        existing.public_key(),
        trusted if trusted is not None else fingerprint(existing),
    )


def test_legitimate_rotation_accepted():
    existing, proposed, record = setup_rotation()
    assert verify(record, existing) is True


def test_forged_signature_rejected():
    existing, proposed, record = setup_rotation()
    attacker = Ed25519PrivateKey.generate()
    forged = signed_rotation(attacker, proposed)
    record["signature"] = forged["signature"]
    assert verify(record, existing) is False


def test_self_approval_rejected():
    existing, proposed, record = setup_rotation()
    record["approved_by"] = " security operations "
    assert verify(record, existing) is False


def test_mismatched_trusted_fingerprint_rejected():
    existing, proposed, record = setup_rotation()
    attacker = Ed25519PrivateKey.generate()
    assert verify(record, existing, fingerprint(attacker)) is False


def test_unchanged_authority_rejected():
    existing, proposed, record = setup_rotation()
    record["proposed_fingerprint"] = fingerprint(existing)
    assert verify(record, existing) is False


def test_malformed_signature_rejected():
    existing, proposed, record = setup_rotation()
    record["signature"] = "not-a-signature"
    assert verify(record, existing) is False


def test_untrusted_existing_key_rejected():
    existing, proposed, record = setup_rotation()
    attacker = Ed25519PrivateKey.generate()
    assert verify(record, attacker, fingerprint(existing)) is False


def test_consumed_rotation_rejected():
    """A previously executed rotation must not be accepted again."""
    existing, proposed, record = setup_rotation()

    result = verify_authority_rotation(
        record,
        existing.public_key(),
        fingerprint(existing),
        frozenset({record["rotation_id"]}),
    )

    assert result is False


def test_unconsumed_rotation_accepted():
    """An otherwise valid, unconsumed rotation remains acceptable."""
    existing, proposed, record = setup_rotation()

    result = verify_authority_rotation(
        record,
        existing.public_key(),
        fingerprint(existing),
        frozenset({"ROT-OTHER"}),
    )

    assert result is True


def test_invalid_replay_registry_rejected():
    """A mutable replay registry must not be accepted."""
    existing, proposed, record = setup_rotation()

    result = verify_authority_rotation(
        record,
        existing.public_key(),
        fingerprint(existing),
        {"ROT-OTHER"},
    )

    assert result is False
