# Macian Authority Lifecycle Security Contract

Status: DESIGN — NOT PRODUCTION APPROVED

## 1. Trust ownership

The verifier's root authority is controlled by the deployment
administrator, independently of evidence submitters.

Evidence submitters cannot provision, replace, revoke or select
the verifier's root authority.

## 2. Initial provisioning

Initial authority installation requires an independently authenticated
administrative process.

The authority fingerprint must be derived from the approved public key.

The installed anchor and its directory chain must satisfy the verifier's
ownership, permission and symbolic-link protections.

Installation must fail closed if an anchor already exists.

## 3. Routine authority rotation

A rotation request identifies:

- Existing authority fingerprint
- Proposed authority fingerprint
- Requester and independent approver
- Approval timestamp
- Rotation reason and unique identifier

The existing trusted authority must authorise the transition.

The proposed authority cannot authorise its own installation.

A separate privileged deployment process must validate and activate
the approved replacement.

## 4. Compromised authority recovery

A compromised authority cannot be trusted to approve its replacement.

Recovery therefore requires an independently established administrative
recovery authority or equivalent protected out-of-band process.

Recovery must not accept credentials supplied solely by an evidence
submitter.

## 5. Audit and rollback

Every successful or rejected authority change must produce an auditable
event without disclosing private signing material.

Rotation must preserve sufficient historical trust evidence to verify
previously issued records under the applicable validity and revocation
policy.

Rollback must require explicit administrative authorisation.

## 6. Release acceptance criteria

Production approval requires:

- Independent initial provisioning
- Authenticated and authorised rotation
- Separation of requester, approver and deployment operator
- Secure, atomic anchor replacement
- Defined compromise-recovery procedure
- Auditable authority lifecycle events
- Adversarial security tests
- Successful full regression testing
- Deployment-specific operational review

This document specifies intended controls. It does not establish that
those controls have been implemented or independently certified.
