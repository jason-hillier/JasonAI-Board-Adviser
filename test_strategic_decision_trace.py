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
