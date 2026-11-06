from dataclasses import dataclass, field
from enum import Enum


class CredibilityVerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    DOCUMENTED = "DOCUMENTED"
    VERIFIED = "VERIFIED"


@dataclass
class EvidenceCredibilityRecord:
    source_identity: str = ""
    source_authority: str = ""
    source_reference: str = ""
    corroborating_references: list[str] = field(default_factory=list)
    verification_status: CredibilityVerificationStatus = (
        CredibilityVerificationStatus.UNVERIFIED
    )
    verified_by: str = ""
    verification_reference: str = ""
