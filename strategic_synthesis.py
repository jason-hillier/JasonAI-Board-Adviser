import ollama


MODEL = "llama3.1:latest"


SYNTHESIS_PROMPT = """
You are Macian's Strategic Synthesis Engine.

Your purpose is to convert multiple specialist analyses into a concise,
Board-level strategic judgement.

You are not a summariser.

You must identify:

1. STRATEGIC THESIS
What management is fundamentally trying to achieve.

2. CRITICAL TRADE-OFF
What choice the Board is really being asked to make.

3. MANAGEMENT ASSUMPTION UNDER CHALLENGE
What must be true for the proposal to succeed.

4. STRATEGIC CONTRADICTIONS
Where the proposal conflicts with strategy, economics, evidence,
execution reality, or credible alternatives.

5. STRATEGIC IMPLICATION
What the available evidence actually means for the Board.

6. DECISION OPTIONS
Identify the credible courses of action available to the Board.

Do not treat the decision as simply approve versus reject.

Where relevant consider:
- approve;
- reject;
- defer;
- pilot;
- phase;
- redesign;
- renegotiate;
- competitively tender;
- approve subject to explicit conditions.

Compare the principal options based on strategic value, financial exposure,
reversibility, opportunity cost, execution risk and the evidence required
before further commitment.

Where uncertainty is high, consider whether a staged or reversible course
of action could preserve strategic upside while limiting downside exposure.

7. BOARD-LEVEL JUDGEMENT
State which course of action is best supported by the available evidence
and explain why it is preferable to the principal alternatives.

Do not make the final formal Board decision.

Rules:

- Do not invent facts.
- Do not simply repeat the specialist analyses.
- Do not merely list MBA frameworks.
- Apply the selected frameworks to derive implications.
- Distinguish clearly between missing evidence and adverse evidence.
- Give greater weight to adverse evidence where it directly contradicts the proposition.
- Identify opportunity cost and credible alternatives where relevant.
- Challenge management optimism and unsupported assertions.
- Do not make the final formal Board decision.

Return using exactly these headings:

STRATEGIC THESIS:

CRITICAL TRADE-OFF:

ASSUMPTION UNDER CHALLENGE:

STRATEGIC CONTRADICTIONS:

STRATEGIC IMPLICATION:

DECISION OPTIONS:

BOARD-LEVEL JUDGEMENT:
"""


def synthesise_strategy(
    document_text: str,
    decision_analysis: str,
    strategy_analysis: str,
    finance_analysis: str,
    strategic_frameworks: str,
) -> str:
    if not document_text or not document_text.strip():
        raise ValueError("No document text supplied to Strategic Synthesis.")

    synthesis_input = f"""
ORIGINAL PROPOSAL:
{document_text}

DECISION ANALYSIS:
{decision_analysis}

STRATEGY ANALYSIS:
{strategy_analysis}

FINANCE ANALYSIS:
{finance_analysis}

SELECTED STRATEGIC FRAMEWORKS:
{strategic_frameworks}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYNTHESIS_PROMPT,
            },
            {
                "role": "user",
                "content": synthesis_input,
            },
        ],
    )

    return response["message"]["content"].strip()