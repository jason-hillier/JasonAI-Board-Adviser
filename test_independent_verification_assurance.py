"""Regression test for Macian's operational assurance demonstration."""

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "independent_verification_assurance.py"


def test_independent_verification_assurance():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout

    report = json.loads(completed.stdout)

    assert report["overall"] == "PASS"
    assert report["trust_provisioning"] == "synthetic_test_fixture"

    expected = {
        "AUTHENTIC": ("PASS", 0),
        "TAMPERED": ("FAIL", 1),
        "UNKNOWN_KEY": ("INDETERMINATE", 2),
        "REVOKED_KEY": ("FAIL", 1),
        "EXPIRED_KEY": ("FAIL", 1),
    }

    results = report["results"]
    assert len(results) == len(expected)

    observed = {result["scenario"]: result for result in results}
    assert set(observed) == set(expected)

    for scenario, (status, exit_code) in expected.items():
        result = observed[scenario]
        assert result["passed"] is True
        assert result["actual_status"] == status
        assert result["actual_exit"] == exit_code
