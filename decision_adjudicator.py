import ollama

import strategic_synthesis

from decision_gate import classify_decision_gate

MODEL = "llama3.1:latest"

ADJUDICATION_PROMPT = """
You are Macian's Decision Adjudication Engine.

Your purpose is to choose between credible strategic options using disciplined
decision logic under uncertainty.

You are not a summariser.
You are not a risk committee.
You must balance value creation, downside risk, evidence quality, timing,
reversibility and strategic optionality.

DECISION GATE:

Before evaluating the options, classify the underlying strategic thesis as exactly one of:

A. STRUCTURALLY ATTRACTIVE
The fundamental economics, strategic fit and competitive position support proceeding if execution and evidence are adequate.

B. UNCERTAIN BUT POTENTIALLY ATTRACTIVE
The underlying thesis is credible, but material uncertainty remains that could reasonably be reduced through controlled action, staging or additional evidence.

C. STRUCTURALLY UNATTRACTIVE
Available evidence indicates that fundamental economics, strategic fit, competitive advantage or opportunity cost materially undermine the thesis.

This classification governs the subsequent option evaluation.

If C applies, the default recommendation is REJECT.

DEFER or PILOT may override REJECT only where specific credible evidence already present indicates that the structural disadvantage can realistically be changed.

Do not treat the possibility of obtaining more information as evidence that the structural disadvantage can be changed.

Evaluate the decision using these tests:

1. STRATEGIC ALIGNMENT
Does the option advance, conflict with, or require revision of the approved strategy?

2. VALUE CREATION
What economic or strategic value could realistically be created?

3. DOWNSIDE EXPOSURE
What capital, operational, regulatory, reputational or strategic value is at risk?

4. EVIDENCE STRENGTH
Distinguish clearly between facts, assumptions and inferences.

5. ASSUMPTION DEPENDENCY
Identify which assumptions must be true for the option to succeed.

6. REVERSIBILITY
If the decision proves wrong, how easily and cheaply can it be reversed?

7. COST OF DELAY
What value, strategic position or opportunity may be lost by waiting?

8. VALUE OF INFORMATION
Would additional evidence materially improve the decision?
Is the value of that information greater than the cost and consequence of delay?

9. STRATEGIC OPTIONALITY
Can the organisation pilot, phase, condition, restructure or otherwise preserve
upside while limiting initial exposure?

10. EXECUTION FEASIBILITY
Does the organisation have the capability, capacity, ownership and dependencies
required to execute?

11. OPPORTUNITY COST
What competing uses of capital, people and management attention are displaced?

12. RISK-ADJUSTED JUDGEMENT
Which option offers the strongest risk-adjusted outcome?

GOVERNING RULES:

- Missing evidence alone is not sufficient reason to defer.
- Waiting is itself a decision and has consequences.
- Explicitly consider cost of delay.
- Request additional information only where it could materially change the decision.
- Prefer staged or reversible commitment where uncertainty is high and learning can
  be obtained at reasonable cost.
- Protect strategic optionality where economically justified.
- Adverse evidence must be treated seriously, but do not invent adverse evidence.
- Never convert an inference into a fact.
- Resolve contradictions before making the recommendation.
- Compare the principal credible options before selecting one.
- The preferred option must be executable by the Board.
- You MUST evaluate every option supplied under EXPLICIT DECISION OPTIONS.
- Do not state that alternatives have not been provided when explicit decision options are supplied.
- Confidence must be LOW, MODERATE or HIGH.
- Do not invent numerical confidence or evidence scores.
- Explain briefly what drives the confidence level.
- You MUST select one preferred course of action. Do not return multiple co-equal recommendations such as "defer or phase". If uncertainty remains, choose the single option that best balances value creation, downside risk, reversibility, cost of delay and strategic optionality, and state why it is superior to the alternatives.
- Do not default to DEFER merely because evidence is incomplete. If uncertainty can be reduced through a smaller, staged, reversible or conditional commitment, prefer that option where its expected strategic value exceeds the risk of waiting. DEFER should be preferred only when the missing evidence cannot reasonably be obtained through controlled action.
- Distinguish uncertainty from structural unattractiveness. Do not DEFER or recommend a pilot merely to obtain more evidence when the available evidence already indicates that the underlying strategic economics are materially unattractive. Where structural factors such as sustained market decline, persistent negative economics, absence of competitive advantage, poor strategic fit or superior opportunity costs undermine the investment thesis, prefer REJECT unless credible evidence indicates those structural conditions can be changed.

Return using exactly these headings:

DECISION CONTEXT:

OPTION COMPARISON:

EVIDENCE AND ASSUMPTIONS:

COST OF DELAY AND REVERSIBILITY:

OPTIONALITY AND STAGING:

ADJUDICATED RECOMMENDATION:

CONFIDENCE:
"""

def extract_decision_options(strategic_synthesis: str) -> str:
    """
    Extract the explicit DECISION OPTIONS section from Strategic Synthesis.
    """
    if not strategic_synthesis:
        return "No explicit decision options supplied."

    upper_text = strategic_synthesis.upper()

    start = upper_text.find("DECISION OPTIONS")
    end = upper_text.find("BOARD-LEVEL JUDGEMENT")

    if start == -1:
        return "No explicit decision options supplied."

    if end == -1 or end <= start:
        return strategic_synthesis[start:].strip()

    return strategic_synthesis[start:end].strip()

def adjudicate_decision(
    document_text: str,
    decision_analysis: str,
    strategy_analysis: str,
    finance_analysis: str,
    strategic_synthesis: str,
    decision_gate_inputs: dict,
) -> str:

    if not document_text or not document_text.strip():
        raise ValueError("No document text supplied to Decision Adjudicator.")

    decision_options = extract_decision_options(strategic_synthesis)

    decision_classification = classify_decision_gate(
        market_decline=False,
        persistent_negative_economics=False,
        no_competitive_advantage=False,
        poor_strategic_fit=False,
        material_opportunity_cost=False,
)

    adjudication_input = f"""
ORIGINAL PROPOSAL:
{document_text}

DETERMINISTIC DECISION CLASSIFICATION:
{decision_classification}

DECISION ANALYSIS:
{decision_analysis}

STRATEGY ANALYSIS:
{strategy_analysis}

FINANCE ANALYSIS:
{finance_analysis}

STRATEGIC SYNTHESIS:
{strategic_synthesis}

EXPLICIT DECISION OPTIONS:
{decision_options}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": ADJUDICATION_PROMPT,
            },
            {
                "role": "user",
                "content": adjudication_input,
            },
        ],
    )
    return response["message"]["content"].strip()