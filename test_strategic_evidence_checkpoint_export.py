"""Tests for portable checkpoint export."""

import json
from dataclasses import replace

import pytest

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_export import export_checkpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    sign_checkpoint,
)


def make_checkpoint():
    return EvidenceAuditCheckpoint(
        checkpoint_id="checkpoint-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )


def test_signed_checkpoint_exports_deterministically():
    private_key, _ = generate_key_pair()
    checkpoint = sign_checkpoint(make_checkpoint(), private_key)

    first = export_checkpoint(checkpoint)
    second = export_checkpoint(checkpoint)

    assert first == second

    package = json.loads(first)

    assert package["format"] == "macian.audit-checkpoint"
    assert package["version"] == 1
    assert package["checkpoint"]["signature"] == checkpoint.signature
    assert package["checkpoint"]["signing_key_id"] == checkpoint.signing_key_id
    assert package["checkpoint"]["verification_status"] == "UNVERIFIED"


def test_unsigned_checkpoint_rejected():
    with pytest.raises(ValueError):
        export_checkpoint(make_checkpoint())


def test_self_declared_verified_checkpoint_rejected():
    private_key, _ = generate_key_pair()
    checkpoint = sign_checkpoint(make_checkpoint(), private_key)

    altered = replace(checkpoint, verification_status="VERIFIED")

    with pytest.raises(ValueError):
        export_checkpoint(altered)
