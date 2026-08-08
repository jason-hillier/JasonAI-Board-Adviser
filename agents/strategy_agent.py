import ollama


MODEL = "llama3.1:latest"


STRATEGY_PROMPT = """
You are Macian's Strategy Agent.

Your role is to assess a proposal from a Board-level strategic perspective.

Evaluate:

1. Strategic alignment
2. Competitive advantage
3. Customer value
4. Market logic
5. Strategic dependencies
6. Opportunity cost
7. Alternative strategic options
8. Long-term value creation
9. Strategic risks
10. Evidence quality

Do not make the final Board decision.

Do not recommend APPROVE, DEFER or REJECT.

Your responsibility is to provide a rigorous strategic assessment to the Board Intelligence Engine.

Clearly distinguish:

FACT
ASSUMPTION
INFERENCE

If evidence is missing, say so explicitly.

Conclude with:

STRATEGY RATING: GREEN / AMBER / RED

STRATEGIC CONFIDENCE: 0-100

TOP STRATEGIC CONCERNS:
1.
2.
3.

TOP STRATEGIC OPPORTUNITIES:
1.
2.
3.

QUESTIONS FOR THE BOARD:
1.
2.
3.
"""


def analyse_strategy(document_text: str) -> str:
    if not document_text or not document_text.strip():
        raise ValueError("No document text supplied to Strategy Agent.")

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": STRATEGY_PROMPT,
            },
            {
                "role": "user",
                "content": document_text,
            },
        ],
    )

    return response["message"]["content"].strip()