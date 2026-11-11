"""Portable verification of Macian audit checkpoints."""

import json
from dataclasses import dataclass, fields

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_engine import validate_checkpoint
from strategic_evidence_checkpoint_export import (
    EXPORT_FORMAT,
    EXPORT_VERSION,
)
from strategic_evidence_checkpoint_trust import (
    verify_trusted_checkpoint,
    verify_checkpoint_key_validity,
)
from strategic_evidence_trusted_keys import TrustedKeyRegistry


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str


def verify_portable_checkpoint(
    package_bytes: bytes,
    registry: TrustedKeyRegistry,
) -> VerificationResult:
    """Verify exported checkpoint against separately supplied trusted keys."""

    if not isinstance(package_bytes, bytes):
        return VerificationResult("FAIL", "INVALID_PACKAGE_TYPE")

    if not isinstance(registry, TrustedKeyRegistry):
        return VerificationResult("FAIL", "INVALID_REGISTRY")

    try:
        def reject_duplicates(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate JSON key")
                result[key] = value
            return result

        package = json.loads(
            package_bytes,
            object_pairs_hook=reject_duplicates,
        )

        if not isinstance(package, dict):
            return VerificationResult("FAIL", "INVALID_SCHEMA")

        if set(package) != {"format", "version", "checkpoint"}:
            return VerificationResult("FAIL", "INVALID_SCHEMA")

        if package["format"] != EXPORT_FORMAT:
            return VerificationResult("FAIL", "UNSUPPORTED_FORMAT")

        if type(package["version"]) is not int or package["version"] != EXPORT_VERSION:
            return VerificationResult("FAIL", "UNSUPPORTED_VERSION")

        data = package["checkpoint"]

        if not isinstance(data, dict):
            return VerificationResult("FAIL", "INVALID_SCHEMA")

        expected_fields = {field.name for field in fields(EvidenceAuditCheckpoint)}

        if set(data) != expected_fields:
            return VerificationResult("FAIL", "INVALID_SCHEMA")

        checkpoint = EvidenceAuditCheckpoint(**data)

        if not validate_checkpoint(checkpoint):
            return VerificationResult("FAIL", "INVALID_CHECKPOINT")

        if not checkpoint.signature or not checkpoint.signing_key_id:
            return VerificationResult("FAIL", "UNSIGNED_CHECKPOINT")

        record = registry.get_trusted_key(checkpoint.signing_key_id)

        if record is None:
            if registry.is_revoked(checkpoint.signing_key_id):
                return VerificationResult("FAIL", "SIGNING_KEY_REVOKED")

            return VerificationResult("INDETERMINATE", "TRUSTED_KEY_UNAVAILABLE")

        if not verify_trusted_checkpoint(checkpoint, registry):
            return VerificationResult("FAIL", "SIGNATURE_OR_TRUST_FAILURE")

        if not verify_checkpoint_key_validity(checkpoint, registry):
            return VerificationResult("FAIL", "KEY_VALIDITY_FAILURE")

        return VerificationResult("PASS", "TRUSTED_SIGNATURE_AND_KEY_VALIDITY")

    except (ValueError, TypeError, UnicodeDecodeError, AttributeError):
        return VerificationResult("FAIL", "MALFORMED_PACKAGE")
