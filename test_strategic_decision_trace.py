from strategic_course_correction import StrategicCourseCorrection
from strategic_decision_trace import build_decision_trace


def test_transform_decision_trace_explains_selected_and_rejected_courses():
    course_correction = StrategicCourseCorrection(
        action="TRANSFORM",
        strategy_challenge=False,
        rationale=(
            "Strategic intent remains valid, but structural capability "
            "gaps prevent delivery."
        ),
        confidence="HIGH",
    )

    trace = build_decision_trace(course_correction)

    assert trace.selected_action == "TRANSFORM"
    assert trace.confidence == "HIGH"

    assert trace.selection_rationale
    assert "structural" in trace.selection_rationale.lower()

    assert "RECONSIDER" in trace.rejected_alternatives
    assert trace.rejected_alternatives["RECONSIDER"]

    assert "thesis" in (
        trace.rejected_alternatives["RECONSIDER"].lower()
    )


def test_transform_trace_explains_all_rejected_alternatives():
    course_correction = StrategicCourseCorrection(
        action="TRANSFORM",
        strategy_challenge=False,
        rationale=(
            "Strategic intent remains valid, but structural capability "
            "gaps prevent delivery."
        ),
        confidence="HIGH",
    )

    trace = build_decision_trace(course_correction)

    expected_alternatives = {
        "RECONSIDER",
        "ADAPT",
        "RESEQUENCE",
        "EXECUTE",
    }

    assert set(trace.rejected_alternatives) == expected_alternatives

    assert "thesis" in trace.rejected_alternatives["RECONSIDER"].lower()
    assert "assumption" in trace.rejected_alternatives["ADAPT"].lower()
    assert "sequenc" in trace.rejected_alternatives["RESEQUENCE"].lower()
    assert "execution" in trace.rejected_alternatives["EXECUTE"].lower()


def test_decision_trace_exposes_rule_and_supporting_evidence():
    course_correction = StrategicCourseCorrection(
        action="TRANSFORM",
        strategy_challenge=False,
        rationale=(
            "Strategic intent remains valid, but structural capability "
            "gaps prevent delivery."
        ),
        confidence="HIGH",
    )

    trace = build_decision_trace(course_correction)

    assert trace.decision_rule
    assert "TRANSFORM" in trace.decision_rule

    assert trace.supporting_evidence
    assert isinstance(trace.supporting_evidence, list)


def test_decision_trace_preserves_source_evidence_provenance():
    course_correction = StrategicCourseCorrection(
        action="TRANSFORM",
        strategy_challenge=False,
        rationale=(
            "Strategic intent remains valid, but structural capability "
            "gaps prevent delivery."
        ),
        confidence="HIGH",
    )

    source_evidence = [
        "Digital origination capability: STRUCTURAL gap",
        "Gap persistence: SUSTAINED",
        "Materiality: HIGH",
        "Confidence: HIGH",
    ]

    trace = build_decision_trace(
        course_correction,
        supporting_evidence=source_evidence,
    )

    assert trace.supporting_evidence == source_evidence
    assert "Digital origination capability" in trace.supporting_evidence[0]


def test_decision_trace_supports_structured_evidence_provenance():
    from strategic_decision_trace import EvidenceProvenance

    course_correction = StrategicCourseCorrection(
        action="TRANSFORM",
        strategy_challenge=False,
        rationale=(
            "Structural capability gaps prevent delivery of "
            "the strategic intent."
        ),
        confidence="HIGH",
    )

    provenance = [
        EvidenceProvenance(
            source="Technology Delivery MI",
            evidence_type="CAPABILITY_GAP",
            reference="Digital origination capability",
            finding="Current capability is structurally insufficient.",
            period="FY27 Q2",
            confidence="HIGH",
        ),
    ]

    trace = build_decision_trace(
        course_correction,
        evidence_provenance=provenance,
    )

    assert len(trace.evidence_provenance) == 1

    evidence = trace.evidence_provenance[0]

    assert evidence.source == "Technology Delivery MI"
    assert evidence.evidence_type == "CAPABILITY_GAP"
    assert evidence.reference == "Digital origination capability"
    assert evidence.period == "FY27 Q2"
    assert evidence.confidence == "HIGH"
    assert evidence.finding
