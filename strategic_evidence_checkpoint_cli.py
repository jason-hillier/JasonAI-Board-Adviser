"""Command-line entry point for independent Macian checkpoint verification."""

import argparse
import json
from pathlib import Path

from strategic_evidence_checkpoint_trust_file import load_trust_file
from strategic_evidence_checkpoint_portable_verify import verify_portable_checkpoint




def main():
    parser = argparse.ArgumentParser(
        description="Verify a portable Macian audit checkpoint."
    )
    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to the exported checkpoint JSON file.",
    )
    parser.add_argument(
        "--trust-file",
        required=True,
        help="Path to independently supplied trusted-key information.",
    )
    args = parser.parse_args()

    try:
        registry = load_trust_file(args.trust_file)
        checkpoint_bytes = Path(args.checkpoint).read_bytes()
        result = verify_portable_checkpoint(checkpoint_bytes, registry)
        status, reason = result.status, result.reason
    except (OSError, ValueError, TypeError, KeyError) as exc:
        status, reason = "FAIL", "INVALID_INPUT"

    print(json.dumps({"status": status, "reason": reason}))
    return {"PASS": 0, "FAIL": 1, "INDETERMINATE": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
