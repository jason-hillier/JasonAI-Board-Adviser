from test_governed_trust_fixture import (
    create_governed_trust_files,
    provision_test_authority_anchor,
)
from test_isolated_verifier import run_isolated_verifier
"""End-to-end regression tests for independent checkpoint verification."""

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_export import export_checkpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    get_signing_key_id,
    sign_checkpoint,
)

CLI = Path(__file__).resolve().parent / "strategic_evidence_checkpoint_cli.py"


@pytest.mark.parametrize(
    "tampered,expected_status,expected_exit",
    [
        (False, "PASS", 0),
        (True, "FAIL", 1),
    ],
)
def test_independent_cli_verification(
    tmp_path, tampered, expected_status, expected_exit
):
    private_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-REGRESSION-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    signed = sign_checkpoint(checkpoint, private_key)
    package = json.loads(export_checkpoint(signed))

    if tampered:
        package["checkpoint"]["event_hash"] = "b" * 64

    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(json.dumps(package), encoding="utf-8")

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_path = tmp_path / "trusted_keys.json"
    trust_path.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": key_id,
                "public_key": base64.b64encode(public_bytes).decode("ascii"),
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
            }],
        }),
        encoding="utf-8",
    )

    governance_args = create_governed_trust_files(tmp_path, trust_path)

    verifier_directory = tmp_path / "isolated_verifier"
    verifier_directory.mkdir()

    provision_test_authority_anchor(
        verifier_directory,
        (tmp_path / "authority-public.key").read_bytes(),
    )

    result = run_isolated_verifier(
        verifier_directory,
        CLI,
        [
            "--checkpoint",
            str(checkpoint_path),
            "--trust-file",
            str(trust_path),
            *governance_args,
        ],
    )

    assert result.returncode == expected_exit, result.stderr
    assert json.loads(result.stdout)["status"] == expected_status


def test_missing_files_fail_safely(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--checkpoint",
            str(tmp_path / "missing-checkpoint.json"),
            "--trust-file",
            str(tmp_path / "missing-trust.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "status": "FAIL",
        "reason": "INVALID_INPUT",
    }


def test_cli_rejects_missing_trust_authorisation(tmp_path):
    """A valid checkpoint must not bypass trust-authority governance."""
    private_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-UNAUTHORISED-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_bytes(
        export_checkpoint(sign_checkpoint(checkpoint, private_key))
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_path = tmp_path / "trust.json"
    trust_path.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": key_id,
                "public_key": base64.b64encode(public_bytes).decode("ascii"),
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
            }],
        }),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--checkpoint", str(checkpoint_path),
            "--trust-file", str(trust_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "FAIL"


def test_cli_rejects_substituted_authority_key(tmp_path):
    """An attacker cannot replace the authority key while retaining its pin."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )

    private_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-AUTH-SUBSTITUTION-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_bytes(
        export_checkpoint(sign_checkpoint(checkpoint, private_key))
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_path = tmp_path / "trust.json"
    trust_path.write_text(
        json.dumps({
            "format": "macian.trusted-keys",
            "version": 1,
            "keys": [{
                "key_id": key_id,
                "public_key": base64.b64encode(public_bytes).decode("ascii"),
                "authority": "Macian Audit Authority",
                "valid_from": "2026-01-01T00:00:00+00:00",
            }],
        }),
        encoding="utf-8",
    )

    governance_args = create_governed_trust_files(tmp_path, trust_path)

    attacker_key = Ed25519PrivateKey.generate().public_key()
    attacker_bytes = attacker_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    (tmp_path / "authority-public.key").write_bytes(attacker_bytes)

    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--checkpoint", str(checkpoint_path),
            "--trust-file", str(trust_path),
            *governance_args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "FAIL"


def test_cli_rejects_substituted_authority_and_pin(tmp_path):
    """A self-authorised package must not establish its own root of trust."""
    import hashlib

    private_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-ROOT-SUBSTITUTION-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_bytes(
        export_checkpoint(sign_checkpoint(checkpoint, private_key))
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_path = tmp_path / "trust.json"
    trust_path.write_text(json.dumps({
        "format": "macian.trusted-keys",
        "version": 1,
        "keys": [{
            "key_id": key_id,
            "public_key": base64.b64encode(public_bytes).decode("ascii"),
            "authority": "Macian Audit Authority",
            "valid_from": "2026-01-01T00:00:00+00:00",
        }],
    }), encoding="utf-8")

    governance_args = create_governed_trust_files(tmp_path, trust_path)

    # Simulate an attacker controlling both authority inputs.
    # The test fixture has already generated a self-consistent key and pin.
    authority_bytes = (tmp_path / "authority-public.key").read_bytes()
    assert (tmp_path / "authority-pin.txt").read_text() == (
        hashlib.sha256(authority_bytes).hexdigest()
    )

    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--checkpoint", str(checkpoint_path),
            "--trust-file", str(trust_path),
            *governance_args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1, (
        "Self-provisioned authority credentials were accepted: "
        + result.stdout
    )
    assert json.loads(result.stdout)["status"] == "FAIL"


def test_provisioned_verifier_rejects_attacker_authority(tmp_path):
    """A provisioned verifier must reject attacker-controlled authority keys."""
    from test_governed_trust_fixture import (
        create_governed_trust_files,
        provision_test_authority_anchor,
    )
    from test_isolated_verifier import run_isolated_verifier

    # Use an existing, valid signed checkpoint and trust registry.
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import base64
    import json

    signing_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trust_path = tmp_path / "trust.json"
    trust_path.write_text(json.dumps({
        "format": "macian.trusted-keys",
        "version": 1,
        "keys": [{
            "key_id": key_id,
            "public_key": base64.b64encode(public_bytes).decode("ascii"),
            "authority": "Macian Audit Authority",
            "valid_from": "2026-01-01T00:00:00+00:00",
        }],
    }), encoding="utf-8")

    # Reuse the established valid-checkpoint fixture.
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-AUTHORITY-SUBSTITUTION-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )
    checkpoint_path.write_bytes(
        export_checkpoint(sign_checkpoint(checkpoint, signing_key))
    )

    legitimate = tmp_path / "legitimate"
    legitimate.mkdir()
    legitimate_args = create_governed_trust_files(legitimate, trust_path)

    verifier = tmp_path / "verifier"
    verifier.mkdir()

    provision_test_authority_anchor(
        verifier,
        (legitimate / "authority-public.key").read_bytes(),
    )

    base_args = [
        "--checkpoint", str(checkpoint_path),
        "--trust-file", str(trust_path),
    ]

    accepted = run_isolated_verifier(
        verifier, CLI, base_args + legitimate_args
    )

    assert accepted.returncode == 0, accepted.stderr or accepted.stdout
    assert json.loads(accepted.stdout)["status"] == "PASS"

    attacker = tmp_path / "attacker"
    attacker.mkdir()
    attacker_args = create_governed_trust_files(attacker, trust_path)

    rejected = run_isolated_verifier(
        verifier, CLI, base_args + attacker_args
    )

    assert rejected.returncode == 1, rejected.stderr or rejected.stdout
    assert json.loads(rejected.stdout)["status"] == "FAIL"
