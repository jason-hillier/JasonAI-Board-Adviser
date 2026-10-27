from dataclasses import dataclass, field

from executive_strategic_synthesis import ExecutiveStrategicView


@dataclass(frozen=True)
class BoardInterventionEvidence:
    intervention: str
    dimension: str
    observed_state: str
    implication: str
    confidence: str


@dataclass(frozen=True)
class BoardInterventionSummary:
    primary: str
    complementary: list[str]
    alternatives: list[str]
    unsupported: list[str]
    confidence: str
    rationale: str
    evidence: list[BoardInterventionEvidence] = field(default_factory=list)


@dataclass
class BoardBriefing:
    strategic_position: str
    confidence: str
    executive_summary: str
    board_implication: str
    recommended_response: str
    decision_required: str
    supporting_evidence: str
    strategic_intervention: object = None
    intervention_summary: object = None
    strategic_challenge: object = None

def generate_board_briefing(
    executive_view: ExecutiveStrategicView,
) -> BoardBriefing:
    """
    Convert the governed Executive Strategic View into a Board briefing.

    This layer communicates established strategic intelligence.
    It does not independently alter strategic position, confidence,
    evidence, or the required Board decision.
    """

    return BoardBriefing(
        strategic_position=executive_view.strategic_position,
        confidence=executive_view.confidence,
        executive_summary=executive_view.executive_summary,
        board_implication=executive_view.board_implication,
        recommended_response=executive_view.recommended_response,
        decision_required=executive_view.decision_required,
        supporting_evidence=(
            executive_view.traceability.trigger_evidence or
            executive_view.traceability.primary_issue or
            "No supporting evidence available."
        ),
    )


def build_board_intervention_summary(intervention):
    """
    Translate a governed StrategicInterventionResult into its
    Board-facing presentation without altering the decision.
    """
    return BoardInterventionSummary(
        primary=intervention.primary_intervention,
        complementary=list(intervention.complementary_interventions),
        alternatives=list(intervention.alternative_interventions),
        unsupported=list(intervention.unsupported_interventions),
        confidence=intervention.confidence,
        rationale=intervention.rationale,
    )


def build_board_intervention_evidence(assessment, intervention):
    """
    Translate an assessed strategic condition into Board-facing
    evidence. Does not independently verify the assessment.
    """

    if intervention == "REDESIGN":
        if assessment.operating_model_fit is not False:
            raise ValueError(
                "REDESIGN requires an assessed operating-model gap."
            )

        return BoardInterventionEvidence(
            intervention="REDESIGN",
            dimension="OPERATING_MODEL",
            observed_state="NOT_FIT",
            implication=(
                "The operating model is assessed as not fit "
                "for the strategic requirement."
            ),
            confidence=assessment.confidence,
        )

    if intervention == "MODERNISE":
        if assessment.technology_data_fit is not False:
            raise ValueError(
                "MODERNISE requires an assessed technology/data gap."
            )

        return BoardInterventionEvidence(
            intervention="MODERNISE",
            dimension="TECHNOLOGY_DATA",
            observed_state="NOT_FIT",
            implication=(
                "Technology and data capabilities are assessed "
                "as not fit for the strategic requirement."
            ),
            confidence=assessment.confidence,
        )

    if intervention == "RECONFIGURE":
        if assessment.organisational_boundaries_fit is not False:
            raise ValueError(
                "RECONFIGURE requires an assessed organisational-boundary gap."
            )

        return BoardInterventionEvidence(
            intervention="RECONFIGURE",
            dimension="ORGANISATIONAL_BOUNDARIES",
            observed_state="NOT_FIT",
            implication=(
                "Organisational boundaries are assessed as not fit "
                "for the strategic requirement."
            ),
            confidence=assessment.confidence,
        )

    raise ValueError(
        f"No evidence mapping defined for intervention: {intervention}"
    )


def assemble_board_intervention_evidence(assessment, intervention_result):
    """
    Assemble Board evidence in governed intervention order:
    primary, complementary, then alternatives.

    Evidence describes assessed strategic conditions.
    It does not independently verify those conditions or
    determine which intervention is preferable.
    """
    interventions = [
        intervention_result.primary_intervention,
        *intervention_result.complementary_interventions,
        *intervention_result.alternative_interventions,
    ]

    if intervention_result.primary_intervention == "INSUFFICIENT_EVIDENCE":
        return []

    if len(interventions) != len(set(interventions)):
        raise ValueError(
            "Duplicate interventions in governed intervention result."
        )

    return [
        build_board_intervention_evidence(assessment, intervention)
        for intervention in interventions
    ]
