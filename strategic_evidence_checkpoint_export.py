"""Versioned portable export of Macian audit checkpoints."""

import json
from dataclasses import asdict

from strategic_evidence_checkpoint import EvidenceAuditCheckpoint
from strategic_evidence_checkpoint_engine import validate_checkpoint


EXPORT_FORMAT = "macian.audit-checkpoint"
EXPORT_VERSION = 1


def export_checkpoint(checkpoint: EvidenceAuditCheckpoint) -> bytes:
    """Export a signed checkpoint without asserting independent trust."""

    if not validate_checkpoint(checkpoint):
        raise ValueError("Invalid checkpoint metadata.")

    if not checkpoint.signature or not checkpoint.signing_key_id:
        raise ValueError("A signed checkpoint is required.")

    payload = {
        "format": EXPORT_FORMAT,
        "version": EXPORT_VERSION,
        "checkpoint": asdict(checkpoint),
    }

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
