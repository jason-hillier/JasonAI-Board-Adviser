from strategic_intervention import (
    StrategicInterventionAssessment,
    assess_strategic_intervention,
)


def test_material_technology_deficiency_supports_modernise():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "MODERNISE"
    assert result.confidence == "HIGH"

    assert "MODERNISE" in result.supported_interventions
    assert "REDESIGN" not in result.supported_interventions
    assert "REINVENT" not in result.supported_interventions
    assert "REFOUND" not in result.supported_interventions

    assert result.rationale


def test_structurally_unfit_operating_model_supports_redesign():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REDESIGN"
    assert result.confidence == "HIGH"

    assert "REDESIGN" in result.supported_interventions
    assert "MODERNISE" not in result.supported_interventions
    assert "REINVENT" not in result.supported_interventions
    assert "REFOUND" not in result.supported_interventions

    assert "operating model" in result.rationale.lower()


def test_operating_model_and_technology_gaps_support_compound_intervention():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REDESIGN"
    assert result.complementary_interventions == ["MODERNISE"]

    assert result.supported_interventions == [
        "REDESIGN",
        "MODERNISE",
    ]

    assert "operating model" in result.rationale.lower()
    assert "technology" in result.rationale.lower()
    assert result.confidence == "HIGH"


def test_unfit_organisational_boundaries_support_reconfigure():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=False,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "RECONFIGURE"
    assert result.confidence == "HIGH"

    assert "RECONFIGURE" in result.supported_interventions
    assert "MODERNISE" not in result.supported_interventions
    assert "REDESIGN" not in result.supported_interventions
    assert "REINVENT" not in result.supported_interventions
    assert "REFOUND" not in result.supported_interventions

    assert "boundar" in result.rationale.lower()


def test_invalid_business_model_supports_reinvent():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=False,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REINVENT"
    assert result.confidence == "HIGH"

    assert result.supported_interventions == ["REINVENT"]
    assert "MODERNISE" not in result.supported_interventions
    assert "REDESIGN" not in result.supported_interventions
    assert "RECONFIGURE" not in result.supported_interventions
    assert "REFOUND" not in result.supported_interventions

    assert "business model" in result.rationale.lower()
    assert "value" in result.rationale.lower()


def test_untransformable_incumbent_supports_refound():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=False,
        transformation_economics_viable=False,
        time_to_value_acceptable=False,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REFOUND"
    assert result.confidence == "HIGH"

    assert "REFOUND" in result.supported_interventions
    assert "REINVENT" not in result.supported_interventions

    assert "incumbent" in result.rationale.lower()
    assert "econom" in result.rationale.lower()
    assert "time" in result.rationale.lower()


def test_fit_strategic_architecture_supports_optimise():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "OPTIMISE"
    assert result.confidence == "HIGH"

    assert result.supported_interventions == ["OPTIMISE"]

    assert "MODERNISE" not in result.supported_interventions
    assert "REDESIGN" not in result.supported_interventions
    assert "RECONFIGURE" not in result.supported_interventions
    assert "REINVENT" not in result.supported_interventions
    assert "REFOUND" not in result.supported_interventions

    assert "existing" in result.rationale.lower()
    assert "performance" in result.rationale.lower()


def test_unknown_material_dimension_returns_insufficient_evidence():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=None,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="MODERATE",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "INSUFFICIENT_EVIDENCE"
    assert result.supported_interventions == []
    assert result.complementary_interventions == []
    assert result.confidence == "MODERATE"

    assert "insufficient" in result.rationale.lower()
    assert "operating_model_fit" in result.rationale


def test_intervention_result_exposes_board_option_structure():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REDESIGN"
    assert result.complementary_interventions == ["MODERNISE"]

    assert hasattr(result, "alternative_interventions")
    assert hasattr(result, "unsupported_interventions")


def test_modernise_case_identifies_unsupported_structural_interventions():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=False,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "MODERNISE"

    assert result.unsupported_interventions == [
        "REDESIGN",
        "RECONFIGURE",
        "REINVENT",
        "REFOUND",
    ]

    assert result.alternative_interventions == []


def test_redesign_case_identifies_unsupported_more_structural_interventions():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=False,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REDESIGN"

    assert result.unsupported_interventions == [
        "RECONFIGURE",
        "REINVENT",
        "REFOUND",
    ]

    assert result.complementary_interventions == []
    assert result.alternative_interventions == []


def test_reconfigure_case_identifies_unsupported_interventions():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=False,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "RECONFIGURE"

    assert result.unsupported_interventions == [
        "REDESIGN",
        "REINVENT",
        "REFOUND",
    ]

    assert result.complementary_interventions == []
    assert result.alternative_interventions == []


def test_unfit_business_model_supports_reinvent():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=False,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REINVENT"
    assert result.confidence == "HIGH"

    assert result.supported_interventions == ["REINVENT"]

    assert result.unsupported_interventions == [
        "REFOUND",
    ]

    assert result.complementary_interventions == []
    assert result.alternative_interventions == []

    assert "business model" in result.rationale.lower()


def test_unchangeable_incumbent_with_unviable_transformation_supports_refound():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=False,
        operating_model_fit=False,
        technology_data_fit=False,
        organisational_boundaries_fit=False,
        incumbent_changeable=False,
        transformation_economics_viable=False,
        time_to_value_acceptable=False,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "REFOUND"
    assert result.confidence == "HIGH"

    assert "REFOUND" in result.supported_interventions

    assert result.complementary_interventions == []
    assert result.alternative_interventions == []

    assert "incumbent" in result.rationale.lower()
    assert "economic" in result.rationale.lower()
    assert "time" in result.rationale.lower()


def test_fit_strategic_architecture_supports_optimise():
    assessment = StrategicInterventionAssessment(
        strategic_thesis_valid=True,
        business_model_valid=True,
        operating_model_fit=True,
        technology_data_fit=True,
        organisational_boundaries_fit=True,
        incumbent_changeable=True,
        transformation_economics_viable=True,
        time_to_value_acceptable=True,
        confidence="HIGH",
    )

    result = assess_strategic_intervention(assessment)

    assert result.primary_intervention == "OPTIMISE"
    assert result.confidence == "HIGH"

    assert result.supported_interventions == ["OPTIMISE"]

    assert result.unsupported_interventions == [
        "MODERNISE",
        "REDESIGN",
        "RECONFIGURE",
        "REINVENT",
        "REFOUND",
    ]

    assert result.complementary_interventions == []
    assert result.alternative_interventions == []

    assert "optim" in result.rationale.lower()
