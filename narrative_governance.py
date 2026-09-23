from dataclasses import dataclass, field
import re


STRATEGIC_POSITIONS = {
    "EXECUTE",
    "RESEQUENCE",
    "ADAPT",
    "TRANSFORM",
    "RECONSIDER",
}


@dataclass
class NarrativeValidationResult:
    valid: bool
    unsupported_claims: list[str] = field(default_factory=list)


def _unsupported_claim(
    claim: str,
    governed_content: str,
    generated_narrative: str,
) -> bool:
    return (
        claim in generated_narrative
        and claim not in governed_content
    )


def _extract_governed_position(governed_content: str):
    match = re.search(
        r"strategic position:\s*(EXECUTE|RESEQUENCE|ADAPT|TRANSFORM|RECONSIDER)",
        governed_content,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).upper()

    return None


def _detect_conflicting_position(
    governed_content: str,
    generated_narrative: str,
):
    governed_position = _extract_governed_position(
        governed_content
    )

    if governed_position is None:
        return None

    generated_upper = generated_narrative.upper()

    for position in STRATEGIC_POSITIONS:
        if (
            position != governed_position
            and re.search(
                rf"\b{position}\b",
                generated_upper,
            )
        ):
            return f"strategic position: {position}"

    return None


def _detect_confidence_escalation(
    governed_content: str,
    generated_narrative: str,
):
    confidence_levels = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
    }

    governed_match = re.search(
        r"confidence:\s*(LOW|MODERATE|HIGH)",
        governed_content,
        re.IGNORECASE,
    )

    if governed_match is None:
        return None

    governed_confidence = governed_match.group(1).upper()
    generated_upper = generated_narrative.upper()

    for confidence, level in confidence_levels.items():
        if (
            level > confidence_levels[governed_confidence]
            and re.search(
                rf"\b{confidence}\s+CONFIDENCE\b",
                generated_upper,
            )
        ):
            return f"confidence: {confidence}"

    return None


def validate_narrative_language(
    governed_content: str,
    generated_narrative: str,
) -> NarrativeValidationResult:
    """
    Validate that generated Board narrative does not introduce
    unsupported strategic severity, urgency, or a strategic position
    different from the governed deterministic conclusion.
    """

    governed = governed_content.lower()
    generated = generated_narrative.lower()

    governed_claims = [
        "existential risk",
        "immediate action",
    ]

    unsupported_claims = [
        claim
        for claim in governed_claims
        if _unsupported_claim(
            claim,
            governed,
            generated,
        )
    ]

    conflicting_position = _detect_conflicting_position(
        governed_content,
        generated_narrative,
    )

    if conflicting_position:
        unsupported_claims.append(
            conflicting_position
        )

    confidence_escalation = _detect_confidence_escalation(
        governed_content,
        generated_narrative,
    )

    if confidence_escalation:
        unsupported_claims.append(
            confidence_escalation
        )

    return NarrativeValidationResult(
        valid=not unsupported_claims,
        unsupported_claims=unsupported_claims,
    )
