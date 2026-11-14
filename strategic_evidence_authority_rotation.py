"""Validation of governed Macian root-authority rotation requests."""

import hashlib
import json
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ROTATION_DOMAIN = b"macian.authority-rotation.v1\x00"

REQUIRED_FIELDS = {
    "format",
    "version",
    "rotation_id",
    "existing_fingerprint",
    "proposed_fingerprint",
    "requested_by",
    "approved_by",
    "approved_at",
    "reason",
    "signature",
}


def verify_authority_rotation(
    rotation: dict,
    existing_authority_public_key: Ed25519PublicKey,
    independently_trusted_fingerprint: str,
    consumed_rotation_ids: frozenset[str] = frozenset(),
) -> bool:
    """Validate a rotation against the independently established root."""

    if type(rotation) is not dict or set(rotation) != REQUIRED_FIELDS:
        return False

    if not isinstance(existing_authority_public_key, Ed25519PublicKey):
        return False

    if type(independently_trusted_fingerprint) is not str:
        return False

    if rotation["format"] != "macian.authority-rotation":
        return False

    if type(rotation["version"]) is not int or rotation["version"] != 1:
        return False

    for field in (
        "rotation_id",
        "existing_fingerprint",
        "proposed_fingerprint",
        "requested_by",
        "approved_by",
        "approved_at",
        "reason",
    ):
        if type(rotation[field]) is not str or not rotation[field].strip():
            return False

    fingerprint_pattern = r"[0-9a-f]{64}"

    for fingerprint in (
        rotation["existing_fingerprint"],
        rotation["proposed_fingerprint"],
        independently_trusted_fingerprint,
    ):
        if re.fullmatch(fingerprint_pattern, fingerprint) is None:
            return False

    if type(consumed_rotation_ids) is not frozenset:
        return False

    if rotation["rotation_id"] in consumed_rotation_ids:
        return False

    if rotation["existing_fingerprint"] != independently_trusted_fingerprint:
        return False

    if rotation["existing_fingerprint"] == rotation["proposed_fingerprint"]:
        return False

    if (
        rotation["requested_by"].strip().casefold()
        == rotation["approved_by"].strip().casefold()
    ):
        return False

    actual_fingerprint = hashlib.sha256(
        existing_authority_public_key.public_bytes_raw()
    ).hexdigest()

    if actual_fingerprint != independently_trusted_fingerprint:
        return False

    signed_record = {
        key: value
        for key, value in rotation.items()
        if key != "signature"
    }

    if type(rotation["signature"]) is not bytes:
        return False

    try:
        payload = json.dumps(
            signed_record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        existing_authority_public_key.verify(
            rotation["signature"],
            ROTATION_DOMAIN + payload,
        )

    except (InvalidSignature, ValueError, TypeError):
        return False

    return True
