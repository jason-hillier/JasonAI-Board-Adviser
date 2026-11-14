"""Command-line entry point for independent Macian checkpoint verification."""

import argparse
import json
from pathlib import Path

from strategic_evidence_authority_anchor import require_trusted_authority_fingerprint
from strategic_evidence_checkpoint_trust_file import load_trust_bytes
from strategic_evidence_checkpoint_signing import get_signing_key_id
from strategic_evidence_trust_authority import (
    decode_governed_trust_approval,
    verify_governed_trust_authorisation,
    verify_pinned_authority_key,
)
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
    parser.add_argument(
        "--trust-approval",
        required=False,
        help="Path to the signed trust-authorisation record.",
    )
    parser.add_argument(
        "--authority-key",
        required=False,
        help="Path to the independently provisioned authority public key.",
    )

    args = parser.parse_args()

    try:
        if not all((
            args.trust_approval,
            args.authority_key,
        )):
            raise ValueError("Independent trust authorisation is required.")

        trust_bytes = Path(args.trust_file).read_bytes()
        approval_bytes = Path(args.trust_approval).read_bytes()
        authority_bytes = Path(args.authority_key).read_bytes()

        trusted_fingerprint = require_trusted_authority_fingerprint()


        authority_key = verify_pinned_authority_key(
            authority_bytes,
            trusted_fingerprint,
        )
        authority_key_id = get_signing_key_id(authority_key)

        approval = decode_governed_trust_approval(approval_bytes)

        if not verify_governed_trust_authorisation(
            trust_bytes,
            approval,
            {authority_key_id: authority_key},
        ):
            raise ValueError("Trust configuration is not authorised.")

        registry = load_trust_bytes(trust_bytes)
        checkpoint_bytes = Path(args.checkpoint).read_bytes()
        result = verify_portable_checkpoint(checkpoint_bytes, registry)
        status, reason = result.status, result.reason
    except (OSError, ValueError, TypeError, KeyError) as exc:
        status, reason = "FAIL", "INVALID_INPUT"

    print(json.dumps({"status": status, "reason": reason}))
    return {"PASS": 0, "FAIL": 1, "INDETERMINATE": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
