from typing import List, Dict


FRAMEWORK_LIBRARY: Dict[str, Dict[str, str]] = {
    "drucker": {
        "name": "Peter Drucker Management Lens",
        "use_when": (
            "The decision concerns organisational purpose, customer value, "
            "management effectiveness, accountability, resource allocation, "
            "or whether the organisation is doing the right things."
        ),
        "questions": (
            "What is the business trying to achieve? "
            "Who is the customer? "
            "What does the customer value? "
            "What should management stop doing? "
            "Who is accountable for results?"
        ),
    },
    "porter": {
        "name": "Porter Competitive Strategy",
        "use_when": (
            "The decision concerns competitive advantage, market structure, "
            "industry attractiveness, differentiation, cost position, or entry barriers."
        ),
        "questions": (
            "What source of competitive advantage is created? "
            "Can competitors replicate it? "
            "How does this change bargaining power, rivalry, substitutes, or barriers to entry?"
        ),
    },
    "rumelt": {
        "name": "Rumelt Strategy Kernel",
        "use_when": (
            "The proposal claims to be strategic but may lack a clear diagnosis, "
            "guiding policy, or coherent set of actions."
        ),
        "questions": (
            "What is the core strategic challenge? "
            "What guiding policy addresses it? "
            "Are the proposed actions coherent with that policy?"
        ),
    },
    "vrio": {
        "name": "VRIO / Resource-Based View",
        "use_when": (
            "The decision concerns internal capabilities, proprietary assets, "
            "technology ownership, talent, data, IP, or sustainable advantage."
        ),
        "questions": (
            "Is the capability valuable, rare, difficult to imitate, and organised to capture value?"
        ),
    },
    "ansoff": {
        "name": "Ansoff Growth Matrix",
        "use_when": (
            "The decision concerns growth through new products, new markets, "
            "market penetration, or diversification."
        ),
        "questions": (
            "Is this market penetration, product development, market development, or diversification? "
            "What is the corresponding risk level?"
        ),
    },
    "capital_allocation": {
        "name": "Capital Allocation Lens",
        "use_when": (
            "The decision involves material investment, acquisition, technology spend, "
            "portfolio allocation, or competing uses of capital."
        ),
        "questions": (
            "What is the opportunity cost? "
            "What alternatives exist? "
            "Does expected return exceed the organisation's required return? "
            "Is this the best use of capital?"
        ),
    },
    "scenario_analysis": {
        "name": "Scenario and Downside Analysis",
        "use_when": (
            "The proposal contains material uncertainty in cost, timing, benefits, "
            "market conditions, delivery, or external dependencies."
        ),
        "questions": (
            "What happens in base, downside and severe downside cases? "
            "Which assumptions drive the outcome most?"
        ),
    },
    "premortem": {
        "name": "Pre-Mortem",
        "use_when": (
            "The decision carries meaningful execution risk, transformation risk, "
            "implementation complexity, or management optimism."
        ),
        "questions": (
            "Assume this failed three years from now. What caused the failure? "
            "Which warning signs would have been visible today?"
        ),
    },
    "build_buy_partner": {
        "name": "Build / Buy / Partner",
        "use_when": (
            "The proposal involves technology ownership, outsourcing, strategic sourcing, "
            "platform development, or capability acquisition."
        ),
        "questions": (
            "Must this capability be owned? "
            "What is the strategic benefit of building versus buying or partnering? "
            "What are the lifecycle cost and execution trade-offs?"
        ),
    },
}


def select_frameworks(document_text: str) -> list:
    """
    Select the most relevant strategic frameworks for the proposal.

    Selection is based on decision archetypes and materiality,
    not simple keyword occurrence alone.
    """

    text = document_text.lower()

    scores = {
        "drucker": 0,
        "porter": 0,
        "rumelt": 0,
        "vrio": 0,
        "ansoff": 0,
        "capital_allocation": 0,
        "scenario_analysis": 0,
        "premortem": 0,
        "build_buy_partner": 0,
    }

    # CAPITAL ALLOCATION
    if any(term in text for term in [
        "investment", "capital", "million", "budget",
        "roi", "irr", "payback", "acquisition"
    ]):
        scores["capital_allocation"] += 4

    if any(term in text for term in [
        "alternative", "opportunity cost", "competing use",
        "cheaper", "cost comparison"
    ]):
        scores["capital_allocation"] += 3

    # BUILD / BUY / PARTNER
    if any(term in text for term in [
        "build", "buy", "partner", "supplier", "vendor",
        "platform", "outsourcing", "insourcing", "proprietary"
    ]):
        scores["build_buy_partner"] += 4

    # VRIO / RESOURCE-BASED VIEW
    if any(term in text for term in [
        "capability", "proprietary", "technology ownership",
        "data", "ip", "talent", "competitive advantage"
    ]):
        scores["vrio"] += 3

    # RUMELT STRATEGY KERNEL
    if any(term in text for term in [
        "strategy", "strategic", "priority", "objective",
        "transformation", "direction"
    ]):
        scores["rumelt"] += 4

    if any(term in text for term in [
        "unclear", "not linked", "misalignment", "no rationale"
    ]):
        scores["rumelt"] += 2

    # DRUCKER MANAGEMENT LENS
    if any(term in text for term in [
        "customer", "value", "management", "purpose",
        "accountability", "owner", "leadership"
    ]):
        scores["drucker"] += 3

    # PORTER
    if any(term in text for term in [
        "competitor", "competition", "market share",
        "industry", "pricing", "differentiation",
        "competitive position"
    ]):
        scores["porter"] += 3

    # ANSOFF
    if any(term in text for term in [
        "new market", "new product", "growth",
        "market penetration", "diversification",
        "market development", "product development"
    ]):
        scores["ansoff"] += 3

    # SCENARIO ANALYSIS
    if any(term in text for term in [
        "risk", "downside", "scenario", "uncertainty",
        "contingency", "sensitivity"
    ]):
        scores["scenario_analysis"] += 4

    # PRE-MORTEM
    if any(term in text for term in [
        "delivery", "implementation", "programme",
        "transformation", "milestone", "execution"
    ]):
        scores["premortem"] += 3

    if any(term in text for term in [
        "unproven", "complex", "high risk", "delay",
        "overrun", "failure"
    ]):
        scores["premortem"] += 2

    # Rank by relevance
    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # Select only materially relevant frameworks
    selected = [
        name
        for name, score in ranked
        if score >= 3
    ]

    # Keep the analysis focused
    return selected[:5]


def get_framework_guidance(document_text: str) -> str:
    """
    Return only the framework guidance relevant to the proposal.
    """

    selected = select_frameworks(document_text)

    if not selected:
        return "No specialist strategic framework selected."

    sections = []

    for key in selected:
        framework = FRAMEWORK_LIBRARY[key]
        sections.append(
            f"""
FRAMEWORK: {framework['name']}

USE WHEN:
{framework['use_when']}

KEY QUESTIONS:
{framework['questions']}
""".strip()
        )

    return "\n\n".join(sections)