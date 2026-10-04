from dataclasses import dataclass, field


@dataclass
class StrategicInterventionAssessment:
    strategic_thesis_valid: bool
    business_model_valid: bool
    operating_model_fit: bool
    technology_data_fit: bool
    organisational_boundaries_fit: bool
    incumbent_changeable: bool
    transformation_economics_viable: bool
    time_to_value_acceptable: bool
    confidence: str


@dataclass
class StrategicInterventionResult:
    primary_intervention: str
    supported_interventions: list[str]
    rationale: str
    confidence: str
    complementary_interventions: list[str] = field(default_factory=list)
    alternative_interventions: list[str] = field(default_factory=list)
    unsupported_interventions: list[str] = field(default_factory=list)


def assess_strategic_intervention(
    assessment: StrategicInterventionAssessment,
) -> StrategicInterventionResult:
    """
    Determine which class of strategic intervention is supported
    by the governed strategic evidence.

    Initial rule:
    where the strategy, business model and operating model remain
    valid but enabling technology/data capability is deficient,
    MODERNISE is the appropriate intervention class.
    """

    material_dimensions = {
        "strategic_thesis_valid": assessment.strategic_thesis_valid,
        "business_model_valid": assessment.business_model_valid,
        "operating_model_fit": assessment.operating_model_fit,
        "technology_data_fit": assessment.technology_data_fit,
        "organisational_boundaries_fit": assessment.organisational_boundaries_fit,
        "incumbent_changeable": assessment.incumbent_changeable,
        "transformation_economics_viable": assessment.transformation_economics_viable,
        "time_to_value_acceptable": assessment.time_to_value_acceptable,
    }

    unknown_dimensions = [
        name
        for name, value in material_dimensions.items()
        if value is None
    ]

    if unknown_dimensions:
        return StrategicInterventionResult(
            primary_intervention="INSUFFICIENT_EVIDENCE",
            supported_interventions=[],
            rationale=(
                "There is insufficient evidence to support a governed "
                "strategic intervention recommendation. Unknown material "
                "dimension(s): "
                + ", ".join(unknown_dimensions)
                + "."
            ),
            confidence=assessment.confidence,
            complementary_interventions=[],
        )

    if (
        assessment.strategic_thesis_valid
        and not assessment.business_model_valid
        and not assessment.operating_model_fit
        and not assessment.technology_data_fit
        and not assessment.organisational_boundaries_fit
        and not assessment.incumbent_changeable
        and not assessment.transformation_economics_viable
        and not assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REFOUND",
            supported_interventions=["REFOUND"],
            rationale=(
                "The strategic intent remains valid, but the incumbent "
                "organisation is not credibly changeable into the required "
                "future state. The current business model, operating model, "
                "technology and organisational boundaries are also unfit, "
                "while transformation economics are unviable and the "
                "required time-to-value is unacceptable. Refounding the "
                "organisation on a new structural foundation is therefore "
                "supported over transformation of the incumbent."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and not assessment.business_model_valid
        and assessment.operating_model_fit
        and assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REINVENT",
            supported_interventions=["REINVENT"],
            unsupported_interventions=["REFOUND"],
            rationale=(
                "The strategic thesis remains valid, but the current "
                "business model is no longer fit to deliver the required "
                "strategic outcome. Business-model reinvention is therefore "
                "supported while the incumbent remains changeable and the "
                "economics and time-to-value remain viable."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and not assessment.operating_model_fit
        and not assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REDESIGN",
            complementary_interventions=["MODERNISE"],
            supported_interventions=[
                "REDESIGN",
                "MODERNISE",
            ],
            rationale=(
                "The operating model is structurally unfit to deliver "
                "the strategic outcome and the enabling technology or "
                "data capability is also deficient. Operating-model "
                "redesign is therefore the primary intervention, "
                "supported by technology and data modernisation."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and assessment.operating_model_fit
        and not assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="MODERNISE",
            supported_interventions=["MODERNISE"],
            unsupported_interventions=[
                "REDESIGN",
                "RECONFIGURE",
                "REINVENT",
                "REFOUND",
            ],
            rationale=(
                "The strategic thesis, business model and operating model "
                "remain valid, but enabling technology or data capability "
                "is materially deficient. Modernisation is therefore "
                "supported without requiring structural redesign or "
                "business-model reinvention."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and not assessment.operating_model_fit
        and assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REDESIGN",
            supported_interventions=["REDESIGN"],
            unsupported_interventions=[
                "RECONFIGURE",
                "REINVENT",
                "REFOUND",
            ],
            rationale=(
                "The strategic thesis and business model remain valid, "
                "but the operating model is structurally unfit to deliver "
                "the required strategic outcome. Operating-model redesign "
                "is therefore supported without requiring technology-led "
                "modernisation or business-model reinvention."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and assessment.operating_model_fit
        and assessment.technology_data_fit
        and not assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="RECONFIGURE",
            supported_interventions=["RECONFIGURE"],
            unsupported_interventions=[
                "REDESIGN",
                "REINVENT",
                "REFOUND",
            ],
            rationale=(
                "The strategic thesis, business model, operating model "
                "and enabling capabilities remain viable, but the current "
                "organisational boundaries are not optimal for delivery. "
                "Reconfiguration is therefore supported, requiring the "
                "Board to consider how capabilities and activities should "
                "be assembled, owned, partnered or sourced."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and not assessment.business_model_valid
        and assessment.operating_model_fit
        and assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REINVENT",
            supported_interventions=["REINVENT"],
            rationale=(
                "The strategic opportunity remains valid, but the existing "
                "business model is no longer a viable basis for creating "
                "and capturing value. Business-model reinvention is "
                "therefore supported rather than optimisation, "
                "modernisation or operating-model redesign."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and not assessment.operating_model_fit
        and not assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and not assessment.incumbent_changeable
        and not assessment.transformation_economics_viable
        and not assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="REFOUND",
            supported_interventions=["REFOUND"],
            rationale=(
                "The strategic thesis and underlying business model remain "
                "valid, but the incumbent operating and technology foundations "
                "are no longer credibly changeable. The economics of continued "
                "transformation are not viable and the required strategic value "
                "cannot be delivered within an acceptable time horizon. "
                "Refounding is therefore supported: the Board should consider "
                "establishing a new organisational, operating or technology "
                "foundation rather than continuing to transform the incumbent."
            ),
            confidence=assessment.confidence,
        )

    if (
        assessment.strategic_thesis_valid
        and assessment.business_model_valid
        and assessment.operating_model_fit
        and assessment.technology_data_fit
        and assessment.organisational_boundaries_fit
        and assessment.incumbent_changeable
        and assessment.transformation_economics_viable
        and assessment.time_to_value_acceptable
    ):
        return StrategicInterventionResult(
            primary_intervention="OPTIMISE",
            supported_interventions=["OPTIMISE"],
            unsupported_interventions=[
                "MODERNISE",
                "REDESIGN",
                "RECONFIGURE",
                "REINVENT",
                "REFOUND",
            ],
            rationale=(
                "The strategic thesis, business model, operating model, "
                "technology and data capabilities, and organisational "
                "boundaries remain fundamentally fit. The existing "
                "architecture therefore remains an appropriate basis for "
                "delivery, with performance improvement best achieved "
                "through optimisation rather than structural intervention."
            ),
            confidence=assessment.confidence,
        )

    raise ValueError(
        "Insufficient intervention rules for the supplied assessment."
    )
