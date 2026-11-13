"""Reproducible operational assurance for Macian checkpoint verification."""

import base64
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_export import export_checkpoint
from strategic_evidence_checkpoint_signing import (
    generate_key_pair,
    get_signing_key_id,
    sign_checkpoint,
)

CLI = Path(__file__).resolve().parent / "strategic_evidence_checkpoint_cli.py"


def run_assurance():
    private_key, public_key = generate_key_pair()
    key_id = get_signing_key_id(public_key)

    checkpoint = EvidenceAuditCheckpoint(
        checkpoint_id="MACIAN-ASSURANCE-001",
        sequence_number=1,
        event_hash="a" * 64,
        checkpoint_timestamp="2026-11-08T12:00:00+00:00",
        checkpoint_authority="Macian Audit Authority",
    )

    signed = sign_checkpoint(checkpoint, private_key)
    original = json.loads(export_checkpoint(signed))

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    trusted_key = {
        "key_id": key_id,
        "public_key": base64.b64encode(public_bytes).decode("ascii"),
        "authority": "Macian Audit Authority",
        "valid_from": "2026-01-01T00:00:00+00:00",
    }

    scenarios = [
        ("AUTHENTIC", False, "normal", "PASS", 0),
        ("TAMPERED", True, "normal", "FAIL", 1),
        ("UNKNOWN_KEY", False, "unknown", "INDETERMINATE", 2),
        ("REVOKED_KEY", False, "revoked", "FAIL", 1),
        ("EXPIRED_KEY", False, "expired", "FAIL", 1),
    ]

    results = []

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        for name, tampered, policy, expected_status, expected_exit in scenarios:
            package = json.loads(json.dumps(original))

            if tampered:
                package["checkpoint"]["event_hash"] = "b" * 64

            keys = [dict(trusted_key)]

            if policy == "unknown":
                keys = []
            elif policy == "revoked":
                keys[0]["revoked"] = True
            elif policy == "expired":
                keys[0]["valid_until"] = "2026-06-01T00:00:00+00:00"

            checkpoint_path = root / f"{name}_checkpoint.json"
            trust_path = root / f"{name}_trust.json"

            checkpoint_path.write_text(
                json.dumps(package), encoding="utf-8"
            )

            trust_path.write_text(
                json.dumps({
                    "format": "macian.trusted-keys",
                    "version": 1,
                    "keys": keys,
                }),
                encoding="utf-8",
            )

            completed = subprocess.run(
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

            try:
                output = json.loads(completed.stdout)
            except json.JSONDecodeError:
                output = {
                    "status": "INVALID_OUTPUT",
                    "reason": completed.stderr,
                }

            actual_status = output.get("status")
            passed = (
                actual_status == expected_status
                and completed.returncode == expected_exit
            )

            results.append({
                "scenario": name,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_exit": expected_exit,
                "actual_exit": completed.returncode,
                "reason": output.get("reason"),
                "passed": passed,
            })

    report = {
        "report_format": "macian.independent-verification-assurance",
        "version": 1,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "verification_method": "separate_python_subprocess",
        "trust_provisioning": "synthetic_test_fixture",
        "results": results,
        "overall": "PASS" if all(r["passed"] for r in results) else "FAIL",
    }

    print(json.dumps(report, indent=2))
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(run_assurance())
