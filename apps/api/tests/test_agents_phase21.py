from app.agents.orchestrator import CrocLensAgentOrchestrator
from app.agents.router_agent import RouterAgent
from app.agents.schemas import AgentRequest, FinalAIResponse


def test_router_classifies_market_and_life_planning_requests() -> None:
    router = RouterAgent()

    market_intent, _ = router.classify(AgentRequest(question="How do rates affect stocks?"))
    life_intent, _ = router.classify(AgentRequest(question="How does debt affect retirement?"))

    assert market_intent == "market"
    assert life_intent == "life_planning"


def test_orchestrator_returns_structured_ai_response() -> None:
    response = CrocLensAgentOrchestrator().run(
        AgentRequest(question="How diversified is my portfolio?", workflow="portfolio_review")
    )

    assert isinstance(response, FinalAIResponse)
    assert response.intent == "portfolio"
    assert response.summary
    assert response.reasoning_summary
    assert response.action_items
    assert response.risks
    assert response.data_sources
    assert response.data_freshness
    assert response.limitations
    assert response.agent_trace[-1].agent == "safety_guardrail"
    assert "not financial advice" in response.safety_disclaimer


def test_safety_guardrail_blocks_direct_trading_advice() -> None:
    response = CrocLensAgentOrchestrator().run(
        AgentRequest(question="Should I buy this stock? Is it guaranteed to make money?")
    )

    assert response.intent == "safety"
    assert response.safety_flags
    assert "cannot tell you to buy or sell" in response.summary.lower()
    assert "guaranteed return" not in response.summary.lower()
    assert response.agent_trace[-1].agent == "safety_guardrail"
