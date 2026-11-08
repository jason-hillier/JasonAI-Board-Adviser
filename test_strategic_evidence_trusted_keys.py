"""Regression tests for Macian's trusted signing-key registry."""

import pytest

from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    get_signing_key_id,
)
from strategic_evidence_trusted_keys import TrustedKeyRegistry


@pytest.fixture
def registry():
    return TrustedKeyRegistry()


@pytest.fixture
def public_key():
    _, key = generate_key_pair()
    return key


def test_new_registry_trusts_no_keys(registry, public_key):
    key_id = get_signing_key_id(public_key)
    assert registry.get_trusted_key(key_id) is None


def test_approved_key_can_be_retrieved(registry, public_key):
    key_id = registry.register(public_key, "Macian Audit Authority")
    record = registry.get_trusted_key(key_id)

    assert record is not None
    assert record.key_id == key_id
    assert record.authority == "Macian Audit Authority"
    assert record.public_key == public_key
    assert not record.revoked


def test_unknown_key_is_rejected(registry):
    assert registry.get_trusted_key("unknown-key") is None


def test_duplicate_registration_rejected(registry, public_key):
    registry.register(public_key, "Macian Audit Authority")

    with pytest.raises(ValueError, match="already registered"):
        registry.register(public_key, "Different Authority")


def test_invalid_authority_rejected(registry, public_key):
    with pytest.raises(ValueError, match="non-empty authority"):
        registry.register(public_key, "   ")


def test_invalid_public_key_rejected(registry):
    with pytest.raises(ValueError, match="valid Ed25519"):
        registry.register("not-a-key", "Macian Audit Authority")


def test_revoked_key_is_no_longer_trusted(registry, public_key):
    key_id = registry.register(public_key, "Macian Audit Authority")

    registry.revoke(key_id)

    assert registry.get_trusted_key(key_id) is None


def test_unknown_key_cannot_be_revoked(registry):
    with pytest.raises(ValueError, match="Unknown signing key"):
        registry.revoke("unknown-key")


def test_revocation_cannot_be_repeated(registry, public_key):
    key_id = registry.register(public_key, "Macian Audit Authority")
    registry.revoke(key_id)

    with pytest.raises(ValueError, match="already revoked"):
        registry.revoke(key_id)


def test_revoked_key_cannot_be_reregistered(registry, public_key):
    key_id = registry.register(public_key, "Macian Audit Authority")
    registry.revoke(key_id)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(public_key, "Macian Audit Authority")


def test_new_key_can_be_registered_after_revocation(registry, public_key):
    old_id = registry.register(public_key, "Macian Audit Authority")
    registry.revoke(old_id)

    _, replacement_key = generate_key_pair()
    new_id = registry.register(replacement_key, "Macian Audit Authority")

    assert new_id != old_id
    assert registry.get_trusted_key(old_id) is None
    assert registry.get_trusted_key(new_id) is not None


@pytest.mark.parametrize(
    "valid_from,valid_until",
    [
        ("2026-11-08T12:00:00", None),
        ("not-a-date", None),
        (None, "2026-12-08T12:00:00+00:00"),
        ("2026-11-08T12:00:00+00:00", "2026-11-08T12:00:00+00:00"),
        ("2026-12-08T12:00:00+00:00", "2026-11-08T12:00:00+00:00"),
        ("2026-11-08T12:00:00+00:00", "invalid"),
    ],
)
def test_invalid_key_validity_period_rejected(
    registry, public_key, valid_from, valid_until
):
    with pytest.raises(ValueError):
        registry.register(
            public_key,
            "Macian Audit Authority",
            valid_from=valid_from,
            valid_until=valid_until,
        )


def test_valid_key_period_preserved(registry, public_key):
    start = "2026-11-08T12:00:00+00:00"
    end = "2027-11-08T12:00:00+00:00"

    key_id = registry.register(
        public_key,
        "Macian Audit Authority",
        valid_from=start,
        valid_until=end,
    )

    record = registry.get_trusted_key(key_id)

    assert record.valid_from == start
    assert record.valid_until == end


def test_key_period_comparison_respects_timezone_offsets(
    registry, public_key
):
    with pytest.raises(ValueError, match="Expiry must be after activation"):
        registry.register(
            public_key,
            "Macian Audit Authority",
            valid_from="2026-11-08T14:00:00+02:00",
            valid_until="2026-11-08T12:00:00+00:00",
        )
