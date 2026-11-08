from dataclasses import replace

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    get_signing_key_id,
    sign_checkpoint,
    verify_checkpoint_signature,
)


def make_checkpoint():
    return EvidenceAuditCheckpoint(
        checkpoint_id="CHECKPOINT-001",
        sequence_number=10,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-06T12:00:00+00:00",
        checkpoint_authority="Independent Audit Authority",
    )


def test_checkpoint_signing_and_verification():
    private_key, public_key = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    assert signed.signature
    assert signed.signing_key_id == get_signing_key_id(public_key)
    assert signed.verification_status == "UNVERIFIED"
    assert verify_checkpoint_signature(signed, public_key)


def test_modified_checkpoint_rejected():
    private_key, public_key = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    modified = replace(signed, event_hash="b" * 64)

    assert not verify_checkpoint_signature(modified, public_key)


def test_wrong_public_key_rejected():
    private_key, _ = generate_key_pair()
    _, wrong_public_key = generate_key_pair()

    signed = sign_checkpoint(make_checkpoint(), private_key)

    assert not verify_checkpoint_signature(signed, wrong_public_key)


def test_wrong_expected_key_identifier_rejected():
    private_key, public_key = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    assert not verify_checkpoint_signature(
        signed,
        public_key,
        expected_key_id="incorrect-key-id",
    )


def test_signature_tampering_rejected():
    private_key, public_key = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    modified = replace(signed, signature="invalid-signature")

    assert not verify_checkpoint_signature(modified, public_key)


def test_key_identifier_is_stable():
    _, public_key = generate_key_pair()

    assert get_signing_key_id(public_key) == get_signing_key_id(public_key)


def test_signing_does_not_claim_verification():
    private_key, _ = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    assert signed.verification_status == "UNVERIFIED"


def test_altered_authority_rejected():
    private_key, public_key = generate_key_pair()
    signed = sign_checkpoint(make_checkpoint(), private_key)

    modified = replace(signed, checkpoint_authority="Different Authority")

    assert not verify_checkpoint_signature(modified, public_key)
