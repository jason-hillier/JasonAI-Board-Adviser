"""Independent cryptographic authorisation of Macian trust configurations."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)

from strategic_evidence_checkpoint_signing import get_signing_key_id


TRUST_AUTHORISATION_DOMAIN = b"macian.trust-authorisation.v1\x00"


def verify_trust_authorisation(
    trust_bytes: bytes,
    approval: dict,
    trusted_authorities: dict,
) -> bool:
    """Verify approval against an independently supplied authority key."""

    if not isinstance(trust_bytes, bytes):
        return False

    if not isinstance(approval, dict):
        return False

    if not isinstance(trusted_authorities, dict):
        return False

    if set(approval) != {"authority_key_id", "signature"}:
        return False

    authority_key_id = approval["authority_key_id"]
    signature = approval["signature"]

    if not isinstance(authority_key_id, str):
        return False

    if not isinstance(signature, bytes):
        return False

    public_key = trusted_authorities.get(authority_key_id)

    if not isinstance(public_key, Ed25519PublicKey):
        return False

    if get_signing_key_id(public_key) != authority_key_id:
        return False

    try:
        public_key.verify(
            signature,
            TRUST_AUTHORISATION_DOMAIN + trust_bytes,
        )
    except (InvalidSignature, ValueError):
        return False

    return True


def verify_governed_trust_authorisation(
    trust_bytes: bytes,
    approval: dict,
    trusted_authorities: dict,
) -> bool:
    """Verify a signed APPROVE decision for exact trust-file bytes."""
    import hashlib
    import json

    fields = {
        "format",
        "version",
        "configuration_hash",
        "decision",
        "requested_by",
        "approved_by",
        "approved_at",
        "authority_key_id",
        "signature",
    }

    if type(trust_bytes) is not bytes:
        return False
    if type(approval) is not dict or set(approval) != fields:
        return False
    if type(trusted_authorities) is not dict:
        return False

    if approval["format"] != "macian.trust-approval":
        return False
    if type(approval["version"]) is not int or approval["version"] != 1:
        return False
    if approval["decision"] != "APPROVE":
        return False

    for field in (
        "configuration_hash",
        "requested_by",
        "approved_by",
        "approved_at",
        "authority_key_id",
    ):
        if type(approval[field]) is not str or not approval[field].strip():
            return False

    if type(approval["signature"]) is not bytes:
        return False

    # Enforce separation of duties for governed trust approvals.
    # Case and surrounding whitespace must not bypass this control.
    if (
        approval["requested_by"].strip().casefold()
        == approval["approved_by"].strip().casefold()
    ):
        return False

    expected_hash = hashlib.sha256(trust_bytes).hexdigest()
    if approval["configuration_hash"] != expected_hash:
        return False

    authority_key_id = approval["authority_key_id"]
    public_key = trusted_authorities.get(authority_key_id)

    if not isinstance(public_key, Ed25519PublicKey):
        return False
    if get_signing_key_id(public_key) != authority_key_id:
        return False

    signed_record = {
        key: value
        for key, value in approval.items()
        if key != "signature"
    }

    try:
        payload = json.dumps(
            signed_record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        public_key.verify(
            approval["signature"],
            b"macian.governed-trust-approval.v1\x00" + payload,
        )
    except (InvalidSignature, ValueError, TypeError):
        return False

    return True


def decode_governed_trust_approval(approval_bytes: bytes) -> dict:
    """Decode a governed approval JSON document with strict signature handling."""
    import base64
    import binascii
    import json

    if not isinstance(approval_bytes, bytes):
        raise ValueError("Approval must be bytes.")

    def reject_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate approval JSON field.")
            result[key] = value
        return result

    try:
        approval = json.loads(
            approval_bytes,
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(approval, dict):
            raise ValueError("Approval must be a JSON object.")

        signature = approval.get("signature")
        if not isinstance(signature, str):
            raise ValueError("Approval signature must be Base64 text.")

        decoded = base64.b64decode(signature, validate=True)
        if len(decoded) != 64:
            raise ValueError("Invalid Ed25519 signature length.")

        if base64.b64encode(decoded).decode("ascii") != signature:
            raise ValueError("Noncanonical Base64 signature.")

        return {**approval, "signature": decoded}

    except (UnicodeDecodeError, json.JSONDecodeError,
            binascii.Error, ValueError, TypeError) as exc:
        raise ValueError("Invalid governed trust approval.") from exc


def verify_pinned_authority_key(
    public_key_bytes: bytes,
    expected_fingerprint: str,
) -> Ed25519PublicKey:
    """Validate an authority key against an independently pinned fingerprint."""
    import hashlib

    if type(public_key_bytes) is not bytes or len(public_key_bytes) != 32:
        raise ValueError("Invalid authority public key.")

    if (
        type(expected_fingerprint) is not str
        or len(expected_fingerprint) != 64
        or any(c not in "0123456789abcdef" for c in expected_fingerprint)
    ):
        raise ValueError("Invalid authority fingerprint.")

    actual_fingerprint = hashlib.sha256(public_key_bytes).hexdigest()

    if actual_fingerprint != expected_fingerprint:
        raise ValueError("Authority key does not match pinned fingerprint.")

    try:
        return Ed25519PublicKey.from_public_bytes(public_key_bytes)
    except ValueError as exc:
        raise ValueError("Invalid Ed25519 authority key.") from exc
