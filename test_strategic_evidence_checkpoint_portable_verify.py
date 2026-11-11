"""Tests for portable checkpoint verification."""

import json
from dataclasses import replace

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_export import export_checkpoint
from strategic_evidence_checkpoint_portable_verify import (
    verify_portable_checkpoint,
)
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    sign_checkpoint,
)
from strategic_evidence_trusted_keys import TrustedKeyRegistry


def setup_checkpoint():
    private_key, public_key = generate_key_pair()

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="checkpoint-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    signed = sign_checkpoint(checkpoint, private_key)

    registry = TrustedKeyRegistry()
    registry.register(
        public_key,
        "Macian Audit Authority",
        valid_from="2026-01-01T00:00:00+00:00",
    )

    return signed, registry


def test_valid_portable_checkpoint_passes():
    checkpoint, registry = setup_checkpoint()

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        registry,
    )

    assert result.status == "PASS"


def test_missing_trusted_key_is_indeterminate():
    checkpoint, _ = setup_checkpoint()

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        TrustedKeyRegistry(),
    )

    assert result.status == "INDETERMINATE"


def test_tampered_checkpoint_fails():
    checkpoint, registry = setup_checkpoint()

    package = json.loads(export_checkpoint(checkpoint))
    package["checkpoint"]["event_hash"] = "b" * 64

    result = verify_portable_checkpoint(
        json.dumps(package).encode(),
        registry,
    )

    assert result.status == "FAIL"


def test_self_declared_verification_fails():
    checkpoint, registry = setup_checkpoint()

    package = json.loads(export_checkpoint(checkpoint))
    package["checkpoint"]["verification_status"] = "VERIFIED"

    result = verify_portable_checkpoint(
        json.dumps(package).encode(),
        registry,
    )

    assert result.status == "FAIL"


def test_revoked_key_is_not_accepted():
    checkpoint, registry = setup_checkpoint()

    registry.revoke(checkpoint.signing_key_id)

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        registry,
    )

    assert result.status != "PASS"


def test_expired_signing_key_fails():
    checkpoint, registry = setup_checkpoint()

    record = registry.get_trusted_key(checkpoint.signing_key_id)

    expired_registry = TrustedKeyRegistry()
    expired_registry.register(
        record.public_key,
        "Macian Audit Authority",
        valid_from="2026-01-01T00:00:00+00:00",
        valid_until="2026-11-01T00:00:00+00:00",
    )

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        expired_registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "KEY_VALIDITY_FAILURE"


def test_signing_key_not_yet_active_fails():
    checkpoint, registry = setup_checkpoint()

    record = registry.get_trusted_key(checkpoint.signing_key_id)

    future_registry = TrustedKeyRegistry()
    future_registry.register(
        record.public_key,
        "Macian Audit Authority",
        valid_from="2027-01-01T00:00:00+00:00",
    )

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        future_registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "KEY_VALIDITY_FAILURE"


def test_missing_key_activation_date_fails():
    checkpoint, registry = setup_checkpoint()

    record = registry.get_trusted_key(checkpoint.signing_key_id)

    undated_registry = TrustedKeyRegistry()
    undated_registry.register(
        record.public_key,
        "Macian Audit Authority",
    )

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        undated_registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "KEY_VALIDITY_FAILURE"


def test_revoked_key_returns_explicit_failure():
    checkpoint, registry = setup_checkpoint()

    registry.revoke(checkpoint.signing_key_id)

    result = verify_portable_checkpoint(
        export_checkpoint(checkpoint),
        registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "SIGNING_KEY_REVOKED"


def test_duplicate_json_fields_are_rejected():
    checkpoint, registry = setup_checkpoint()

    package = export_checkpoint(checkpoint).decode("utf-8")

    package = package.replace(
        '"version":1',
        '"version":1,"version":1',
        1,
    )

    result = verify_portable_checkpoint(
        package.encode("utf-8"),
        registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "MALFORMED_PACKAGE"


def test_malformed_json_is_rejected():
    _, registry = setup_checkpoint()

    result = verify_portable_checkpoint(
        b'{"format":"macian.audit-checkpoint","version":1,',
        registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "MALFORMED_PACKAGE"


def test_unsupported_export_version_fails():
    checkpoint, registry = setup_checkpoint()

    package = json.loads(export_checkpoint(checkpoint))
    package["version"] = 999

    result = verify_portable_checkpoint(
        json.dumps(package).encode("utf-8"),
        registry,
    )

    assert result.status == "FAIL"
    assert result.reason == "UNSUPPORTED_VERSION"
