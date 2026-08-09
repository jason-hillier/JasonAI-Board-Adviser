from typing import Dict


def evaluate_decision_policy(
    document_text: str,
    decision_analysis: str,
    strategy_analysis: str,
    finance_analysis: str,
) -> Dict[str, str]:
    """
    Apply Macian's Board decision policy.

    This layer distinguishes between:
    - missing evidence, which may justify DEFER; and
    - adverse evidence, which may justify REJECT.

    The policy does not replace specialist analysis.
    It governs how that evidence should influence the final Board decision.
    """

    combined_evidence = f"""
ORIGINAL PROPOSAL:
{document_text}

DECISION ANALYSIS:
{decision_analysis}

STRATEGY ANALYSIS:
{strategy_analysis}

FINANCE ANALYSIS:
{finance_analysis}
"""

    policy = """
MACIAN DECISION POLICY

Assess the evidence, not management's optimism.

Classify evidence into:

1. SUPPORTING EVIDENCE
Evidence supporting the proposition.

2. MISSING EVIDENCE
Information required but not supplied.

3. ADVERSE EVIDENCE
Evidence actively weakening or contradicting the proposition.

DECISION RULES:

APPROVE:
Evidence positively supports proceeding and material risks are acceptable.

APPROVE WITH CONDITIONS:
The underlying case is sound, but specific controllable conditions must
be satisfied.

DEFER:
The proposition could reasonably be attractive, but material evidence
needed to decide is genuinely unavailable.

REJECT:
Existing evidence demonstrates that the proposition is materially
unattractive, strategically inconsistent, economically inferior,
disproportionately risky, or unjustified relative to credible alternatives.

CRITICAL RULE:

Do not classify adverse evidence as missing evidence.

The theoretical possibility that management could produce additional
information is not, by itself, sufficient reason to DEFER.

Where credible evidence already demonstrates a materially superior
alternative, strategic misalignment, disproportionate cost, or
unacceptable risk, REJECT must be seriously considered.

Evaluate opportunity cost explicitly.

Evaluate credible alternatives explicitly.

Evaluate whether the proposed expenditure is proportionate to the
incremental value created.

Return:

DECISION:
APPROVE / APPROVE WITH CONDITIONS / DEFER / REJECT

DECISION RATIONALE:

SUPPORTING EVIDENCE:

ADVERSE EVIDENCE:

MISSING EVIDENCE:

DECISION-CRITICAL FACTORS:
"""

    return {
        "policy": policy,
        "evidence": combined_evidence,
    }