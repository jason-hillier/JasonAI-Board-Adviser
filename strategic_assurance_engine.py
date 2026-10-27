from strategic_assurance import (
    AssuranceDimension,
    StrategicAssuranceAssessment,
)
from strategic_assurance_status import (
    AssuranceCategory,
    AssuranceStatus,
)


def assess_strategic_assurance(
    evidence_by_category: dict[str, list[str]],
) -> StrategicAssuranceAssessment:
    """
    Perform an initial deterministic evidence-presence assessment.

    Supplied evidence is classified as UNVERIFIED.
    This function does not independently validate evidence,
    determine contradictions or substantiate recommendations.
    """
    dimensions = []
    critical_gaps = []
    board_questions = []

    for category in AssuranceCategory:
        evidence = evidence_by_category.get(category.value, [])
        references = [
            item.strip()
            for item in evidence
            if isinstance(item, str) and item.strip()
        ]

        if references:
            status = AssuranceStatus.UNVERIFIED
            rationale = (
                "Evidence has been supplied but has not "
                "been independently verified."
            )
            requirements = [
                "Verify the reliability and relevance of the evidence."
            ]
        else:
            status = AssuranceStatus.MISSING_EVIDENCE
            rationale = "No supporting evidence has been supplied."
            requirements = [
                "Provide traceable supporting evidence."
            ]
            critical_gaps.append(category.value)
            board_questions.append(
                f"What evidence supports {category.value.lower().replace('_', ' ')}?"
            )

        dimensions.append(
            AssuranceDimension(
                category=category.value,
                status=status.value,
                rationale=rationale,
                evidence_references=references,
                assurance_requirements=requirements,
            )
        )

    overall_status = (
        AssuranceStatus.MISSING_EVIDENCE.value
        if critical_gaps
        else AssuranceStatus.UNVERIFIED.value
    )

    return StrategicAssuranceAssessment(
        dimensions=dimensions,
        overall_status=overall_status,
        critical_gaps=critical_gaps,
        board_questions=board_questions,
    )
