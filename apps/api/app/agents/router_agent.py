from app.agents.schemas import AgentIntent, AgentRequest, AgentTrace


UNSAFE_TERMS = [
    "should i buy",
    "should i sell",
    "tell me what to buy",
    "tell me what to sell",
    "guaranteed",
    "will make money",
    "best investment",
    "ignore previous instructions",
    "reveal your system prompt",
    "act as my financial advisor",
]


class RouterAgent:
    agent_name = "router_agent"

    def classify(self, request: AgentRequest) -> tuple[AgentIntent, AgentTrace]:
        lowered = request.question.lower()
        if any(term in lowered for term in UNSAFE_TERMS):
            intent: AgentIntent = "safety"
        elif request.workflow == "portfolio_review" or any(
            term in lowered for term in ["portfolio", "allocation", "diversification", "net worth", "risk", "liquidity"]
        ):
            intent = "portfolio"
        elif any(term in lowered for term in ["market", "stock", "etf", "crypto", "bitcoin", "rates", "inflation"]):
            intent = "market"
        elif any(term in lowered for term in ["retirement", "401", "ira", "debt", "loan", "mortgage", "goal"]):
            intent = "life_planning"
        elif any(term in lowered for term in ["tax", "wash sale", "capital gain", "loss harvesting"]):
            intent = "tax"
        elif "journal" in lowered or request.workflow == "action_plan":
            intent = "journal"
        else:
            intent = "education"

        return intent, AgentTrace(
            agent="router_agent",
            status="used",
            input_summary=request.question,
            output_summary=f"Routed to {intent}.",
            tools_used=[],
        )
