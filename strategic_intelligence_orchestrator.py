class StrategicIntelligenceOrchestrator:
    """
    Coordinate the governed strategic intelligence pipeline.

    The orchestrator does not make strategic decisions.
    It delegates intelligence and governance to the
    established specialist layers.
    """

    pipeline = [
        "STRATEGIC_ASSESSMENT",
        "BOARD_SYNTHESIS",
        "PORTFOLIO_INTELLIGENCE",
        "COURSE_CORRECTION",
        "EXECUTIVE_SYNTHESIS",
        "BOARD_BRIEFING",
        "NARRATIVE_ENHANCEMENT",
        "NARRATIVE_GOVERNANCE",
    ]

    def run_governed_executive_pipeline(self, executive_view):
        """
        Pass an already-governed executive strategic view into
        the downstream Board communication pipeline.

        This boundary must not alter strategic position,
        confidence, decision requirements or traceability.
        """
        return executive_view
