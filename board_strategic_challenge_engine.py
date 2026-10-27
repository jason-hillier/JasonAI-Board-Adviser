from board_strategic_challenge import (
	BoardStrategicChallenge,
	StrategicChallengeFinding,
)


def assess_board_strategic_challenge(
	management_recommendation: str,
	supporting_evidence: str,
	alternative_options: list[str] | None = None,
) -> BoardStrategicChallenge:
	"""
	Assess whether a management recommendation provides sufficient
	information for constructive Board scrutiny.

	This is an initial, deterministic challenge layer.
	It does not independently verify evidence or change decisions.
	"""
	findings = []
	unresolved_assumptions = []
	assurance_requirements = []

	alternatives = list(alternative_options or [])

	if not management_recommendation.strip():
		findings.append(
			StrategicChallengeFinding(
				category="STRATEGIC_RATIONALE",
				challenge="No management recommendation has been provided.",
				evidence="Management recommendation is missing.",
				severity="HIGH",
				board_question=(
					"What decision is management asking the Board to make?"
				),
			)
		)

	if not supporting_evidence.strip():
		findings.append(
			StrategicChallengeFinding(
				category="EVIDENCE",
				challenge="The recommendation lacks supporting evidence.",
				evidence="No supporting evidence has been supplied.",
				severity="HIGH",
				board_question=(
					"What evidence supports the proposed course of action?"
				),
			)
		)
		assurance_requirements.append(
			"Provide traceable evidence supporting the recommendation."
		)

	if not alternatives:
		findings.append(
			StrategicChallengeFinding(
				category="STRATEGIC_ALTERNATIVES",
				challenge="No alternative courses of action are documented.",
				evidence="The alternatives list is empty.",
				severity="MEDIUM",
				board_question=(
					"Which credible alternatives were considered, "
					"and why were they rejected?"
				),
			)
		)
		unresolved_assumptions.append(
			"Management has demonstrated that its preferred option "
			"is superior to credible alternatives."
		)

	return BoardStrategicChallenge(
		findings=findings,
		unresolved_assumptions=unresolved_assumptions,
		alternative_options=alternatives,
		assurance_requirements=assurance_requirements,
		overall_assessment=(
			"CHALLENGE_REQUIRED" if findings else "NO_GAPS_IDENTIFIED"
		),
	)
