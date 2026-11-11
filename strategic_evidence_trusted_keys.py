"""Trusted Ed25519 public-key registry for Macian checkpoints."""

from dataclasses import dataclass, replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from strategic_evidence_checkpoint_signing import get_signing_key_id
from strategic_evidence_key_time import parse_key_timestamp


@dataclass(frozen=True)
class TrustedSigningKey:
    key_id: str
    authority: str
    public_key: Ed25519PublicKey
    revoked: bool = False
    valid_from: str | None = None
    valid_until: str | None = None
    revoked_at: str | None = None


class TrustedKeyRegistry:
    """Explicitly approved signing keys; unknown keys are never trusted."""

    def __init__(self):
        self._keys: dict[str, TrustedSigningKey] = {}

    def register(
        self,
        public_key: Ed25519PublicKey,
        authority: str,
        valid_from: str | None = None,
        valid_until: str | None = None,
    ) -> str:
        if not isinstance(public_key, Ed25519PublicKey):
            raise ValueError("A valid Ed25519 public key is required.")

        if not isinstance(authority, str) or not authority.strip():
            raise ValueError("A non-empty authority is required.")

        start = (
            parse_key_timestamp(valid_from)
            if valid_from is not None
            else None
        )
        end = (
            parse_key_timestamp(valid_until)
            if valid_until is not None
            else None
        )

        if end is not None and start is None:
            raise ValueError("Expiry requires an activation timestamp.")

        if start is not None and end is not None and end <= start:
            raise ValueError("Expiry must be after activation.")

        key_id = get_signing_key_id(public_key)

        if key_id in self._keys:
            raise ValueError("Signing key is already registered.")

        self._keys[key_id] = TrustedSigningKey(
            key_id=key_id,
            authority=authority,
            public_key=public_key,
            valid_from=valid_from,
            valid_until=valid_until,
        )
        return key_id

    def get_trusted_key(self, key_id: str) -> TrustedSigningKey | None:
        if not isinstance(key_id, str):
            return None

        record = self._keys.get(key_id)

        if record is None or record.revoked:
            return None

        return record

    def is_revoked(self, key_id: str) -> bool:
        """Return whether a registered signing key is revoked."""
        if not isinstance(key_id, str):
            return False

        record = self._keys.get(key_id)
        return record is not None and record.revoked

    def revoke(self, key_id: str) -> None:
        record = self._keys.get(key_id)

        if record is None:
            raise ValueError("Unknown signing key.")

        if record.revoked:
            raise ValueError("Signing key is already revoked.")

        self._keys[key_id] = replace(
            record,
            revoked=True,
        )
