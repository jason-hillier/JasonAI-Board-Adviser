from dataclasses import dataclass
from typing import Literal, Optional


EvidenceType = Literal["FACT", "ASSUMPTION", "INFERENCE", "GAP"]
Materiality = Literal["LOW", "MEDIUM", "HIGH"]


@dataclass
class EvidenceItem:
    statement: str
    evidence_type: EvidenceType
    materiality: Materiality
    source: Optional[str] = None
    confidence: Optional[str] = None

@dataclass
class DecisionOption:
    name: str
    description: str
    strategic_value: Materiality
    downside_exposure: Materiality
    reversibility: Materiality
    execution_risk: Materiality
    opportunity_cost: Materiality
    evidence_required: Optional[str] = None

@dataclass
class Finding:
    title: str
    description: str
    materiality: Materiality
    evidence_type: EvidenceType
    source: Optional[str] = None
    confidence: Optional[str] = None

@dataclass
class Risk:
    title: str
    description: str
    materiality: Materiality
    likelihood: Materiality
    impact: Materiality
    source: Optional[str] = None

@dataclass
class Opportunity:
    title: str
    description: str
    materiality: Materiality
    strategic_value: Materiality
    evidence_type: Optional[EvidenceType] = None
    source: Optional[str] = None

@dataclass
class TradeOff:
    title: str
    description: str
    benefit: str
    cost: str
    materiality: Materiality

@dataclass
class Recommendation:
    decision: str
    rationale: str
    confidence: Literal["LOW", "MODERATE", "HIGH"]
    conditions: Optional[str] = None
    evidence_gaps: Optional[str] = None

@dataclass
class DecisionCase:
    title: str
    proposal: str
    evidence: list[EvidenceItem]
    findings: list[Finding]
    risks: list[Risk]
    opportunities: list[Opportunity]
    tradeoffs: list[TradeOff]
    options: list[DecisionOption]
    recommendation: Optional[Recommendation] = None