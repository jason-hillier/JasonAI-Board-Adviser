from dataclasses import dataclass, field
from enum import Enum


class VerificationActivity(str, Enum):
    DOCUMENT_EXISTENCE = "DOCUMENT_EXISTENCE"
    SOURCE_AUTHENTICITY = "SOURCE_AUTHENTICITY"
    CLAIM_SUBSTANTIATION = "CLAIM_SUBSTANTIATION"


class VerificationOutcome(str, Enum):
    NOT_PERFORMED = "NOT_PERFORMED"
    INCONCLUSIVE = "INCONCLUSIVE"
    PASSED = "PASSED"
    FAILED = "FAILED"


@dataclass
class EvidenceVerificationRecord:
    evidence_reference: str
    activity: VerificationActivity
    outcome: VerificationOutcome = VerificationOutcome.NOT_PERFORMED
    reviewer_identity: str = ""
    verification_method: str = ""
    verification_reference: str = ""
    verification_date: str = ""
    limitations: list[str] = field(default_factory=list)


@dataclass
class TrustedEvidenceVerificationAssessment:
    evidence_reference: str
    records: list[EvidenceVerificationRecord] = field(
        default_factory=list
    )
    overall_status: str = "UNVERIFIED"
    limitations: list[str] = field(default_factory=list)
