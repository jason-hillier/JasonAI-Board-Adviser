"""Tests for checkpoint signing-key validity windows."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    sign_checkpoint,
)
from strategic_evidence_checkpoint_trust import (
    verify_checkpoint_key_validity,
)
from strategic_evidence_trusted_keys import TrustedKeyRegistry


BASE = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)


def timestamp(offset_seconds: int) -> str:
    return (BASE + timedelta(seconds=offset_seconds)).isoformat()


def make_checkpoint(
    checkpoint_time: str,
    valid_from: str | None,
    valid_until: str | None,
) -> tuple[EvidenceAuditCheckpoint, TrustedKeyRegistry]:
    private_key, public_key = generate_key_pair()
    registry = TrustedKeyRegistry()

    registry.register(
        public_key,
        "Macian Audit Authority",
        valid_from=valid_from,
        valid_until=valid_until,
    )

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id=str(uuid4()),
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp=checkpoint_time,
        checkpoint_authority="Macian Audit Authority",
    )

    return sign_checkpoint(checkpoint, private_key), registry


@pytest.mark.parametrize(
    "checkpoint_time,valid_from,valid_until,expected",
    [
        (timestamp(-1), timestamp(0), timestamp(100), False),
        (timestamp(0), timestamp(0), timestamp(100), True),
        (timestamp(99), timestamp(0), timestamp(100), True),
        (timestamp(100), timestamp(0), timestamp(100), False),
        (timestamp(50), None, None, False),
        (timestamp(1000), timestamp(0), None, True),
    ],
)
def test_checkpoint_key_validity_boundaries(
    checkpoint_time, valid_from, valid_until, expected
):
    checkpoint, registry = make_checkpoint(
        checkpoint_time,
        valid_from,
        valid_until,
    )

    assert verify_checkpoint_key_validity(checkpoint, registry) is expected


def test_malformed_checkpoint_timestamp_rejected():
    checkpoint, registry = make_checkpoint(
        "not-a-date",
        timestamp(0),
        timestamp(100),
    )

    assert verify_checkpoint_key_validity(checkpoint, registry) is False


def test_revoked_key_rejected_even_within_validity_period():
    checkpoint, registry = make_checkpoint(
        timestamp(50),
        timestamp(0),
        timestamp(100),
    )

    registry.revoke(checkpoint.signing_key_id)

    assert verify_checkpoint_key_validity(checkpoint, registry) is False
