from pathlib import Path
"""Test-only fixtures for independently governed trust configurations."""

import base64
import hashlib
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from strategic_evidence_checkpoint_signing import get_signing_key_id


def provision_test_authority_anchor(verifier_directory, authority_bytes):
    """Provision a test verifier's trusted authority before verification."""
    verifier_directory = Path(verifier_directory).resolve()
    production_directory = Path(__file__).resolve().parent

    if verifier_directory == production_directory:
        raise ValueError("Cannot provision test authority into production source.")

    if not verifier_directory.is_dir():
        raise ValueError("Isolated test verifier directory does not exist.")

    fingerprint = hashlib.sha256(authority_bytes).hexdigest()
    anchor_path = verifier_directory / "strategic_evidence_authority_anchor.py"

    if anchor_path.exists():
        raise ValueError("Test authority anchor already provisioned.")

    anchor_path.write_text(
        "TRUSTED_AUTHORITY_FINGERPRINT = " + repr(fingerprint) + "\n"
        + "def require_trusted_authority_fingerprint():\n"
        + "    return TRUSTED_AUTHORITY_FINGERPRINT\n",
        encoding="utf-8",
    )
    return fingerprint


def create_governed_trust_files(tmp_path, trust_path):
    """Create an independently signed approval for exact trust-file bytes."""
    authority_private = Ed25519PrivateKey.generate()
    authority_public = authority_private.public_key()

    authority_bytes = authority_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    authority_key_id = get_signing_key_id(authority_public)
    trust_bytes = trust_path.read_bytes()

    approval = {
        "format": "macian.trust-approval",
        "version": 1,
        "configuration_hash": hashlib.sha256(trust_bytes).hexdigest(),
        "decision": "APPROVE",
        "requested_by": "Macian Test Requester",
        "approved_by": "Macian Independent Test Authority",
        "approved_at": "2026-11-08T12:00:00+00:00",
        "authority_key_id": authority_key_id,
    }

    payload = json.dumps(
        approval,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    signature = authority_private.sign(
        b"macian.governed-trust-approval.v1\x00" + payload
    )

    approval["signature"] = base64.b64encode(signature).decode("ascii")

    approval_path = tmp_path / "trust-approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    authority_path = tmp_path / "authority-public.key"
    authority_path.write_bytes(authority_bytes)

    pin_path = tmp_path / "authority-pin.txt"
    pin_path.write_text(
        hashlib.sha256(authority_bytes).hexdigest(),
        encoding="ascii",
    )

    return [
        "--trust-approval", str(approval_path),
        "--authority-key", str(authority_path),
    ]
