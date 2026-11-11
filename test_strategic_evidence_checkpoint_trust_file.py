"""Security tests for the independent trust-file loader."""

import json

import pytest

from strategic_evidence_checkpoint_trust_file import load_trust_file


def test_unsupported_trust_file_version_fails(tmp_path):
    trust_file = tmp_path / "trusted_keys.json"

    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 999,
            "keys": [],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported trust-file version"):
        load_trust_file(str(trust_file))


def test_duplicate_trust_file_fields_are_rejected(tmp_path):
    trust_file = tmp_path / "trusted_keys.json"

    trust_file.write_text(
        '{"format":"macian.trusted-keys","version":1,"version":1,"keys":[]}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate JSON key"):
        load_trust_file(str(trust_file))


def test_valid_trust_file_loads_successfully(tmp_path):
    import base64

    from cryptography.hazmat.primitives import serialization
    from strategic_evidence_checkpoint_signing import (
        generate_key_pair,
        get_signing_key_id,
    )

    _, public_key = generate_key_pair()

    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    key_id = get_signing_key_id(public_key)

    trust_file = tmp_path / "trusted_keys.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": key_id,
                "public_key": base64.b64encode(raw_key).decode("ascii"),
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
            }],
        }),
        encoding="utf-8",
    )

    registry = load_trust_file(str(trust_file))

    assert registry.get_trusted_key(key_id) is not None
    assert registry.get_trusted_key(key_id).authority == "Macian Audit Authority"


def test_non_boolean_revocation_is_rejected(tmp_path):
    import base64

    from cryptography.hazmat.primitives import serialization
    from strategic_evidence_checkpoint_signing import (
        generate_key_pair,
        get_signing_key_id,
    )

    _, public_key = generate_key_pair()
    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_file = tmp_path / "invalid_revocation.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": get_signing_key_id(public_key),
                "public_key": base64.b64encode(raw_key).decode("ascii"),
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
                "revoked": "false",
            }],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="revoked must be a boolean"):
        load_trust_file(str(trust_file))


def test_unexpected_top_level_field_is_rejected(tmp_path):
    trust_file = tmp_path / "unexpected_top_level.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [],
            "allow_unverified": True,
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unexpected trust-file fields"):
        load_trust_file(str(trust_file))


def test_unexpected_key_field_is_rejected(tmp_path):
    trust_file = tmp_path / "unexpected_key_field.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": "example",
                "public_key": "example",
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
                "bypass_signature": True,
            }],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unexpected trusted-key fields"):
        load_trust_file(str(trust_file))


def test_duplicate_trusted_key_identifier_is_rejected(tmp_path):
    import base64

    from cryptography.hazmat.primitives import serialization
    from strategic_evidence_checkpoint_signing import (
        generate_key_pair,
        get_signing_key_id,
    )

    _, public_key = generate_key_pair()
    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    entry = {
        "key_id": get_signing_key_id(public_key),
        "public_key": base64.b64encode(raw_key).decode("ascii"),
        "authority": "Macian Audit Authority",
        "valid_from": "2026-01-01T00:00:00+00:00",
    }

    trust_file = tmp_path / "duplicate_keys.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [entry, dict(entry)],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate trusted-key identifier"):
        load_trust_file(str(trust_file))


@pytest.mark.parametrize(
    "field,value",
    [
        ("authority", None),
        ("authority", 123),
        ("valid_from", None),
        ("valid_from", 123),
        ("public_key", None),
        ("public_key", 123),
    ],
)
def test_invalid_trusted_key_attribute_is_rejected(tmp_path, field, value):
    import base64

    from cryptography.hazmat.primitives import serialization
    from strategic_evidence_checkpoint_signing import (
        generate_key_pair,
        get_signing_key_id,
    )

    _, public_key = generate_key_pair()

    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    entry = {
        "key_id": get_signing_key_id(public_key),
        "public_key": base64.b64encode(raw_key).decode("ascii"),
        "authority": "Macian Audit Authority",
        "valid_from": "2026-01-01T00:00:00+00:00",
    }
    entry[field] = value

    trust_file = tmp_path / "invalid_attribute.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [entry],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid trusted-key attribute"):
        load_trust_file(str(trust_file))


@pytest.mark.parametrize(
    "field,value",
    [
        ("valid_from", "not-a-date"),
        ("valid_from", "2026-13-01T00:00:00+00:00"),
        ("valid_from", "2026-01-01T00:00:00"),
        ("valid_until", "not-a-date"),
        ("valid_until", "2026-01-01T00:00:00"),
    ],
)
def test_invalid_key_validity_timestamp_is_rejected(tmp_path, field, value):
    import base64

    from cryptography.hazmat.primitives import serialization
    from strategic_evidence_checkpoint_signing import (
        generate_key_pair,
        get_signing_key_id,
    )

    _, public_key = generate_key_pair()
    raw_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    entry = {
        "key_id": get_signing_key_id(public_key),
        "public_key": base64.b64encode(raw_key).decode("ascii"),
        "authority": "Macian Audit Authority",
        "valid_from": "2026-01-01T00:00:00+00:00",
    }
    entry[field] = value

    trust_file = tmp_path / "invalid_timestamp.json"
    trust_file.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [entry],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid trusted-key timestamp"):
        load_trust_file(str(trust_file))
