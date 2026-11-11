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

    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--checkpoint",
            str(checkpoint_path),
            "--trust-file",
            str(trust_path),
        ],
        capture_output=True,
        text=True,
        check=False,
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
