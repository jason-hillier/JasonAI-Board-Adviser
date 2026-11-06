from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceQualityCriterion:
    category: str
    description: str
    required_information: tuple[str, ...]


EVIDENCE_QUALITY_CRITERIA = (
    EvidenceQualityCriterion(
        category="CREDIBILITY",
        description="Assess source authority and provenance.",
        required_information=(
            "source_identity",
            "source_authority",
            "corroboration",
        ),
    ),
    EvidenceQualityCriterion(
        category="RELEVANCE",
        description="Assess alignment with the strategic claim.",
        required_information=(
            "strategic_claim",
            "evidence_relationship",
        ),
    ),
    EvidenceQualityCriterion(
        category="COMPLETENESS",
        description="Assess coverage and material omissions.",
        required_information=(
            "scope",
            "material_gaps",
            "alternative_evidence",
        ),
    ),
    EvidenceQualityCriterion(
        category="CONSISTENCY",
        description="Assess contradictions and reconciliation.",
        required_information=(
            "conflicting_evidence",
            "reconciliation",
        ),
    ),
    EvidenceQualityCriterion(
        category="CURRENCY",
        description="Assess evidence recency and validity.",
        required_information=(
            "evidence_date",
            "decision_horizon",
        ),
    ),
)
