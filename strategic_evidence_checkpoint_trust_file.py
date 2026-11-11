"""Load independently provisioned trusted signing keys."""

import base64
import binascii
import json
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from strategic_evidence_trusted_keys import TrustedKeyRegistry


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate_timestamp(value, field):
    if type(value) is not str or not value.strip():
        raise ValueError(f"Invalid trusted-key attribute: {field}")

    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("Timezone required")
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(
            f"Invalid trusted-key timestamp: {field}"
        ) from exc

    return parsed


def load_trust_file(path: str) -> TrustedKeyRegistry:
    """Load a strictly validated, independently maintained key registry."""

    data = json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicates,
    )

    if not isinstance(data, dict):
        raise ValueError("Trust file must contain a JSON object.")

    if data.get("format") != "macian.trusted-keys":
        raise ValueError("Unsupported trust-file format.")

    if type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("Unsupported trust-file version.")

    if not isinstance(data.get("keys"), list):
        raise ValueError("Trust file must contain a keys list.")

    if set(data) != {"format", "version", "keys"}:
        raise ValueError("Unexpected trust-file fields.")

    allowed = {
        "key_id", "public_key", "authority",
        "valid_from", "valid_until", "revoked",
    }
    required = {"key_id", "public_key", "authority", "valid_from"}

    registry = TrustedKeyRegistry()
    seen_key_ids = set()

    for entry in data["keys"]:
        if not isinstance(entry, dict):
            raise ValueError("Invalid trusted-key entry.")

        if not required.issubset(entry):
            raise ValueError("Missing required trusted-key fields.")

        if set(entry) - allowed:
            raise ValueError("Unexpected trusted-key fields.")

        for field in ("key_id", "public_key", "authority"):
            value = entry[field]
            if type(value) is not str or not value.strip():
                raise ValueError(f"Invalid trusted-key attribute: {field}")

        start = _validate_timestamp(entry["valid_from"], "valid_from")

        valid_until = entry.get("valid_until")
        if valid_until is not None:
            end = _validate_timestamp(valid_until, "valid_until")
            if end <= start:
                raise ValueError(
                    "Invalid trusted-key timestamp: expiry must follow activation"
                )

        revoked = entry.get("revoked", False)
        if type(revoked) is not bool:
            raise ValueError("revoked must be a boolean.")

        claimed_key_id = entry["key_id"]
        if claimed_key_id in seen_key_ids:
            raise ValueError("Duplicate trusted-key identifier.")
        seen_key_ids.add(claimed_key_id)

        try:
            raw_key = base64.b64decode(
                entry["public_key"], validate=True
            )
            public_key = Ed25519PublicKey.from_public_bytes(raw_key)
        except (ValueError, TypeError, binascii.Error) as exc:
            raise ValueError(
                "Invalid trusted-key attribute: public_key"
            ) from exc

        key_id = registry.register(
            public_key,
            entry["authority"],
            valid_from=entry["valid_from"],
            valid_until=valid_until,
        )

        if claimed_key_id != key_id:
            raise ValueError("Trusted-key identifier mismatch.")

        if revoked:
            registry.revoke(key_id)

    return registry
