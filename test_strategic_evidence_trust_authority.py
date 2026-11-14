"""Security tests for independently authorised trust configurations."""

import pytest

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from strategic_evidence_checkpoint_signing import get_signing_key_id
from strategic_evidence_trust_authority import verify_trust_authorisation


def make_approval(trust_bytes, private_key):
    public_key = private_key.public_key()
    return {
        "authority_key_id": get_signing_key_id(public_key),
        "signature": private_key.sign(
            b"macian.trust-authorisation.v1\x00" + trust_bytes
        ),
    }


def test_authorised_trust_configuration_passes():
    private_key = Ed25519PrivateKey.generate()
    trust_bytes = b'{"keys":[]}'
    approval = make_approval(trust_bytes, private_key)

    assert verify_trust_authorisation(
        trust_bytes,
        approval,
        {approval["authority_key_id"]: private_key.public_key()},
    )


def test_modified_trust_configuration_is_rejected():
    private_key = Ed25519PrivateKey.generate()
    approval = make_approval(b'{"keys":[]}', private_key)

    assert not verify_trust_authorisation(
        b'{"keys":["unauthorised"]}',
        approval,
        {approval["authority_key_id"]: private_key.public_key()},
    )


def test_unknown_authority_is_rejected():
    private_key = Ed25519PrivateKey.generate()
    trust_bytes = b'{"keys":[]}'
    approval = make_approval(trust_bytes, private_key)

    assert not verify_trust_authorisation(
        trust_bytes,
        approval,
        {},
    )


def test_invalid_signature_is_rejected():
    private_key = Ed25519PrivateKey.generate()
    trust_bytes = b'{"keys":[]}'
    approval = make_approval(trust_bytes, private_key)
    approval["signature"] = b"\x00" * 64

    assert not verify_trust_authorisation(
        trust_bytes,
        approval,
        {approval["authority_key_id"]: private_key.public_key()},
    )


def test_approval_metadata_cannot_be_modified():
    """Changing governance metadata must invalidate authorisation."""
    private_key = Ed25519PrivateKey.generate()
    trust_bytes = b'{"keys":[]}'
    approval = make_approval(trust_bytes, private_key)

    approval["decision"] = "APPROVE"
    approval["requested_by"] = "key-custodian"
    approval["approved_by"] = "independent-authority"
    approval["version"] = 1
    approval["approved_at"] = "2026-11-13T12:00:00+00:00"

    trusted = {
        approval["authority_key_id"]: private_key.public_key()
    }

    assert not verify_trust_authorisation(
        trust_bytes,
        approval,
        trusted,
    )


def test_governance_decision_is_cryptographically_bound():
    """An authority signature must authenticate the governance decision."""
    import hashlib
    import json

    from strategic_evidence_trust_authority import (
        verify_governed_trust_authorisation,
    )

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    trust_bytes = b'{"keys":[]}'

    record = {
        "format": "macian.trust-approval",
        "version": 1,
        "configuration_hash": hashlib.sha256(trust_bytes).hexdigest(),
        "decision": "APPROVE",
        "requested_by": "key-custodian",
        "approved_by": "independent-authority",
        "approved_at": "2026-11-13T12:00:00+00:00",
        "authority_key_id": get_signing_key_id(public_key),
    }

    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    signature = private_key.sign(
        b"macian.governed-trust-approval.v1\x00" + payload
    )

    approval = {
        **record,
        "signature": signature,
    }

    trusted = {
        record["authority_key_id"]: public_key,
    }

    assert verify_governed_trust_authorisation(
        trust_bytes, approval, trusted
    )

    tampered = {
        **approval,
        "decision": "REVOKE",
    }

    assert not verify_governed_trust_authorisation(
        trust_bytes, tampered, trusted
    )


def test_governed_approval_json_decoder():
    import base64
    import json
    import pytest

    from strategic_evidence_trust_authority import (
        decode_governed_trust_approval,
    )

    signature = bytes(range(64))
    encoded = base64.b64encode(signature).decode("ascii")

    valid = json.dumps({
        "signature": encoded,
        "decision": "APPROVE",
    }).encode("utf-8")

    decoded = decode_governed_trust_approval(valid)

    assert decoded["signature"] == signature
    assert decoded["decision"] == "APPROVE"

    invalid_documents = [
        b'{"signature": "invalid!"}',
        b'{"signature": "YWJj"}',
        b'{"signature": 123}',
        b'{"signature": null}',
        b'{"signature": "AAAA", "signature": "BBBB"}',
        b'[]',
        b'not-json',
    ]

    for document in invalid_documents:
        with pytest.raises(ValueError):
            decode_governed_trust_approval(document)


def test_pinned_authority_key_validation():
    import hashlib
    import pytest

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from strategic_evidence_trust_authority import (
        verify_pinned_authority_key,
    )

    def raw_public_key():
        return Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    trusted_key = raw_public_key()
    substituted_key = raw_public_key()
    fingerprint = hashlib.sha256(trusted_key).hexdigest()

    verified = verify_pinned_authority_key(trusted_key, fingerprint)
    assert isinstance(verified, Ed25519PublicKey)

    with pytest.raises(ValueError):
        verify_pinned_authority_key(substituted_key, fingerprint)

    with pytest.raises(ValueError):
        verify_pinned_authority_key(trusted_key, "0" * 63)

    with pytest.raises(ValueError):
        verify_pinned_authority_key(b"invalid", fingerprint)

    with pytest.raises(ValueError):
        verify_pinned_authority_key(trusted_key, fingerprint.upper())


def test_governed_trust_rejects_cryptographically_valid_self_approval():
    import hashlib
    import json

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from strategic_evidence_checkpoint_signing import get_signing_key_id
    from strategic_evidence_trust_authority import verify_governed_trust_authorisation

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    trust_bytes = b'{"keys":[]}'
    authority_key_id = get_signing_key_id(public_key)

    record = {
        "format": "macian.trust-approval",
        "version": 1,
        "configuration_hash": hashlib.sha256(trust_bytes).hexdigest(),
        "decision": "APPROVE",
        "requested_by": "same-person",
        "approved_by": "same-person",
        "approved_at": "2026-11-13T12:00:00+00:00",
        "authority_key_id": authority_key_id,
    }

    payload = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    signature = private_key.sign(
        b"macian.governed-trust-approval.v1\x00" + payload
    )

    approval = {**record, "signature": signature}
    trusted = {authority_key_id: public_key}

    assert not verify_governed_trust_authorisation(
        trust_bytes, approval, trusted
    )

    # A valid signature must not bypass identity normalisation.
    for requester, approver in [
        ("same-person", "SAME-PERSON"),
        (" same-person ", "same-person"),
        ("Same-Person", " same-person "),
    ]:
        record["requested_by"] = requester
        record["approved_by"] = approver

        payload = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        signed_approval = {
            **record,
            "signature": private_key.sign(
                b"macian.governed-trust-approval.v1\x5cx00" + payload
            ),
        }

        assert not verify_governed_trust_authorisation(
            trust_bytes, signed_approval, trusted
        )
