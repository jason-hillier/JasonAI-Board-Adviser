from strategic_evidence_quality import (
    EvidenceQualityDimension,
    StrategicEvidenceQualityAssessment,
)
from strategic_evidence_quality_criteria import EVIDENCE_QUALITY_CRITERIA
from strategic_evidence_quality_status import EvidenceQualityStatus


def assess_strategic_evidence_quality(
    information_by_category: dict[str, dict[str, str]],
) -> StrategicEvidenceQualityAssessment:
    """
    Identify missing information needed for evidence-quality assessment.

    This initial engine does not independently verify evidence,
    assess source reliability, or award positive quality ratings.
    """
    dimensions = []
    material_weaknesses = []
    board_questions = []

    for criterion in EVIDENCE_QUALITY_CRITERIA:
        information = information_by_category.get(criterion.category, {})

        missing_fields = [
            field
            for field in criterion.required_information
            if not isinstance(information.get(field), str)
            or not information[field].strip()
        ]

        if missing_fields:
            status = EvidenceQualityStatus.INSUFFICIENT_INFORMATION.value
            rationale = (
                "Required information is missing for evidence-quality "
                "assessment."
            )
            limitations = [
                f"Missing required information: {field}"
                for field in missing_fields
            ]
            material_weaknesses.append(criterion.category)
            board_questions.append(
                f"What information is available to assess "
                f"{criterion.category.lower()}?"
            )
        else:
            status = EvidenceQualityStatus.NOT_ASSESSED.value
            rationale = (
                "Required information has been supplied, but evidence "
                "quality has not yet been evaluated."
            )
            limitations = [
                "Information has not been independently verified.",
                "No substantive evidence-quality judgement has been made.",
            ]

        dimensions.append(
            EvidenceQualityDimension(
                category=criterion.category,
                status=status,
                rationale=rationale,
                evidence_references=[],
                limitations=limitations,
            )
        )

    overall_status = (
        EvidenceQualityStatus.INSUFFICIENT_INFORMATION.value
        if material_weaknesses
        else EvidenceQualityStatus.NOT_ASSESSED.value
    )

    return StrategicEvidenceQualityAssessment(
        dimensions=dimensions,
        overall_status=overall_status,
        material_weaknesses=material_weaknesses,
        board_questions=board_questions,
    )
