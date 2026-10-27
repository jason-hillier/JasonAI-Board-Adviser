from dataclasses import dataclass, field


@dataclass
class StrategicChallengeFinding:
	category: str
	challenge: str
	evidence: str
	severity: str
	board_question: str


@dataclass
class BoardStrategicChallenge:
	findings: list[StrategicChallengeFinding] = field(
		default_factory=list
	)
	unresolved_assumptions: list[str] = field(
		default_factory=list
	)
	alternative_options: list[str] = field(
		default_factory=list
	)
	assurance_requirements: list[str] = field(
		default_factory=list
	)
	overall_assessment: str = "NOT_ASSESSED"
