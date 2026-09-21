from dataclasses import dataclass, field

from strategic_course_correction import StrategicCourseCorrection


@dataclass
class EvidenceProvenance:
    source: str
    evidence_type: str
    reference: str
    finding: str
    period: str
    confidence: str


@dataclass
class StrategicDecisionTrace:
    selected_action: str
    confidence: str
    selection_rationale: str
    rejected_alternatives: dict[str, str] = field(
        default_factory=dict
    )
    decision_rule: str = ""
    supporting_evidence: list[str] = field(default_factory=list)
    evidence_provenance: list[EvidenceProvenance] = field(
        default_factory=list
    )


def build_decision_trace(
    course_correction: StrategicCourseCorrection,
    supporting_evidence: list[str] | None = None,
    evidence_provenance: list[EvidenceProvenance] | None = None,
) -> StrategicDecisionTrace:
    rejected_alternatives: dict[str, str] = {}

    if course_correction.action == "TRANSFORM":
        rejected_alternatives = {
            "RECONSIDER": (
                "The strategic thesis has not been invalidated. "
                "The evidence supports retaining the underlying "
                "strategic direction."
            ),
            "ADAPT": (
                "No strategic assumption has been invalidated at the "
                "threshold required to adapt the strategy itself."
            ),
            "RESEQUENCE": (
                "Changing the sequence or timing of strategic objectives "
                "is insufficient to resolve the structural capability gap."
            ),
            "EXECUTE": (
                "Normal execution correction is insufficient because "
                "the constraint is structural rather than solely a "
                "delivery-performance issue."
            ),
        }

    return StrategicDecisionTrace(
        selected_action=course_correction.action,
        confidence=course_correction.confidence,
        selection_rationale=course_correction.rationale,
        rejected_alternatives=rejected_alternatives,
        decision_rule=(
            f"{course_correction.action}: "
            f"{course_correction.rationale}"
        ),
        supporting_evidence=(
            supporting_evidence
            if supporting_evidence is not None
            else [course_correction.rationale]
        ),
        evidence_provenance=(
            evidence_provenance
            if evidence_provenance is not None
            else []
        ),
    )
