from decision_engine import analyse_document_structured
from decision_models import DecisionCase, EvidenceItem, Finding, Risk
from dataclasses import asdict
from decision_models import DecisionCase, EvidenceItem, Finding, Risk, Opportunity, TradeOff, DecisionOption

def test_structured_decision_engine_returns_decision_case():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    assert isinstance(result, DecisionCase)
    assert len(result.evidence) > 0
    assert len(result.findings) > 0
    assert all(isinstance(item, EvidenceItem) for item in result.evidence)
    assert all(isinstance(item, Finding) for item in result.findings)

    from dataclasses import asdict


def test_decision_case_serializes():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    serialized = asdict(result)

    assert serialized["title"] == "Untitled Decision"
    assert serialized["proposal"]
    assert isinstance(serialized["evidence"], list)
    assert isinstance(serialized["findings"], list)

def test_structured_decision_engine_returns_risks():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    assert isinstance(result, DecisionCase)
    assert isinstance(result.risks, list)

    if result.risks:
        assert all(isinstance(item, Risk) for item in result.risks)

def test_structured_decision_engine_returns_opportunities():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    assert isinstance(result, DecisionCase)
    assert isinstance(result.opportunities, list)

    if result.opportunities:
        assert all(isinstance(item, Opportunity) for item in result.opportunities)

def test_structured_decision_engine_returns_tradeoffs():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    assert isinstance(result, DecisionCase)
    assert isinstance(result.tradeoffs, list)

    if result.tradeoffs:
        assert all(isinstance(item, TradeOff) for item in result.tradeoffs)

def test_structured_decision_engine_returns_options():
    result = analyse_document_structured(
        "Management proposes investing £10 million in a new digital platform. "
        "The existing platform remains operational but is nearing capacity. "
        "No ROI analysis has been completed and delivery ownership is unclear."
    )

    assert isinstance(result, DecisionCase)
    assert isinstance(result.options, list)

    if result.options:
        assert all(isinstance(item, DecisionOption) for item in result.options)