import pytest

from dataclasses import replace

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_engine import validate_checkpoint


@pytest.fixture
def valid_checkpoint():
    return EvidenceAuditCheckpoint(
        checkpoint_id="CHECKPOINT-001",
        sequence_number=10,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-06T12:00:00+00:00",
        checkpoint_authority="Independent Audit Authority",
    )


def test_valid_checkpoint_accepted(valid_checkpoint):
    assert validate_checkpoint(valid_checkpoint)


@pytest.mark.parametrize(
    "field,value",
    [
        ("checkpoint_id", ""),
        ("sequence_number", 0),
        ("sequence_number", True),
        ("event_hash", "invalid"),
        ("event_hash", "z" * 64),
        ("checkpoint_timestamp", ""),
        ("checkpoint_authority", ""),
        ("signature", None),
        ("verification_status", "TRUSTED"),
    ],
)
def test_invalid_checkpoint_rejected(valid_checkpoint, field, value):
    invalid = replace(valid_checkpoint, **{field: value})
    assert not validate_checkpoint(invalid)


def test_unverified_checkpoint_not_mistaken_for_verified(valid_checkpoint):
    assert valid_checkpoint.verification_status == "UNVERIFIED"
    assert validate_checkpoint(valid_checkpoint)


def test_non_checkpoint_object_rejected():
    assert not validate_checkpoint({"checkpoint_id": "CHECKPOINT-001"})


@pytest.mark.parametrize("status", ["VERIFIED", "REJECTED"])
def test_self_declared_verification_status_rejected(
    valid_checkpoint, status
):
    checkpoint = replace(
        valid_checkpoint,
        verification_status=status,
    )

    assert not validate_checkpoint(checkpoint)
