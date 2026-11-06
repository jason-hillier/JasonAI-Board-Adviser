from strategic_evidence_verification import (
    EvidenceVerificationRecord,
    TrustedEvidenceVerificationAssessment,
    VerificationActivity,
    VerificationOutcome,
)


def assess_trusted_evidence_verification(
    evidence_reference: str,
    records: list[EvidenceVerificationRecord],
) -> TrustedEvidenceVerificationAssessment:
    """Assess submitted verification records without authenticating them."""

    limitations = []

    if not isinstance(evidence_reference, str) or not evidence_reference.strip():
        limitations.append("Evidence reference is missing or invalid.")

    valid_records = []

    if not isinstance(records, list):
        limitations.append(
            "Verification records must be supplied as a list."
        )
        records = []

    for record in records:
        if not isinstance(record, EvidenceVerificationRecord):
            limitations.append("Invalid verification record supplied.")
            continue

        if record.evidence_reference != evidence_reference:
            limitations.append("Verification record references different evidence.")
            continue

        if not isinstance(record.activity, VerificationActivity):
            limitations.append("Invalid verification activity.")
            continue

        valid_records.append(record)

        for attribute in (
            "reviewer_identity",
            "verification_method",
            "verification_reference",
            "verification_date",
        ):
            value = getattr(record, attribute)
            if not isinstance(value, str) or not value.strip():
                limitations.append(
                    f"{record.activity.value}: missing or invalid "
                    f"{attribute}."
                )

        if record.outcome == VerificationOutcome.PASSED:
            limitations.append(
                f"{record.activity.value}: declared PASSED outcome "
                "has not been independently authenticated."
            )
        elif record.outcome == VerificationOutcome.FAILED:
            limitations.append(
                f"{record.activity.value}: reported FAILED outcome "
                "requires review."
            )
        elif record.outcome == VerificationOutcome.INCONCLUSIVE:
            limitations.append(
                f"{record.activity.value}: verification is inconclusive."
            )
        elif record.outcome == VerificationOutcome.NOT_PERFORMED:
            limitations.append(
                f"{record.activity.value}: verification not performed."
            )
        else:
            limitations.append(
                f"{record.activity.value}: invalid verification outcome."
            )

    recorded_activities = {record.activity for record in valid_records}

    for activity in VerificationActivity:
        matching_records = [
            record for record in valid_records
            if record.activity == activity
        ]

        if len(matching_records) > 1:
            limitations.append(
                f"{activity.value}: duplicate verification records "
                "require reconciliation."
            )

    for activity in VerificationActivity:
        if activity not in recorded_activities:
            limitations.append(
                f"{activity.value}: no verification record supplied."
            )

    limitations.append(
        "No trusted mechanism has authenticated the verification records."
    )

    return TrustedEvidenceVerificationAssessment(
        evidence_reference=evidence_reference,
        records=valid_records,
        overall_status="UNVERIFIED",
        limitations=limitations,
    )
