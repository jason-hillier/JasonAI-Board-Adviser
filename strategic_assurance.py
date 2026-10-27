from dataclasses import dataclass, field


@dataclass
class AssuranceDimension:
    category: str
    status: str = "NOT_ASSESSED"
    rationale: str = ""
    evidence_references: list[str] = field(default_factory=list)
    assurance_requirements: list[str] = field(default_factory=list)


@dataclass
class StrategicAssuranceAssessment:
    dimensions: list[AssuranceDimension] = field(default_factory=list)
    overall_status: str = "NOT_ASSESSED"
    critical_gaps: list[str] = field(default_factory=list)
    board_questions: list[str] = field(default_factory=list)
