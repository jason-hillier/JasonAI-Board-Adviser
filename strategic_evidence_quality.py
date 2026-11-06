from dataclasses import dataclass, field


@dataclass
class EvidenceQualityDimension:
    category: str
    status: str = "NOT_ASSESSED"
    rationale: str = ""
    evidence_references: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class StrategicEvidenceQualityAssessment:
    dimensions: list[EvidenceQualityDimension] = field(
        default_factory=list
    )
    overall_status: str = "NOT_ASSESSED"
    material_weaknesses: list[str] = field(default_factory=list)
    board_questions: list[str] = field(default_factory=list)
