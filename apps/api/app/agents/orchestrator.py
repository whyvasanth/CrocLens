from app.agents.action_plan_agent import ActionPlanAgent
from app.agents.decision_journal_agent import DecisionJournalAgent
from app.agents.life_planning_agent import LifePlanningAgent
from app.agents.market_research_agent import MarketResearchAgent
from app.agents.router_agent import RouterAgent
from app.agents.safety_guardrail_agent import SafetyGuardrailAgent
from app.agents.schemas import AgentIntent, AgentRequest, AgentResult, FinalAIResponse
from app.agents.tax_awareness_agent import TaxAwarenessAgent
from app.agents.wealth_analyst_agent import WealthAnalystAgent
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


class CrocLensAgentOrchestrator:
    def __init__(self) -> None:
        self.router = RouterAgent()
        self.specialists = {
            "portfolio": WealthAnalystAgent(),
            "market": MarketResearchAgent(),
            "life_planning": LifePlanningAgent(),
            "tax": TaxAwarenessAgent(),
            "journal": DecisionJournalAgent(),
            "education": WealthAnalystAgent(),
            "safety": WealthAnalystAgent(),
        }
        self.action_plan = ActionPlanAgent()
        self.safety = SafetyGuardrailAgent()

    def run(self, request: AgentRequest) -> FinalAIResponse:
        intent, router_trace = self.router.classify(request)
        specialist = self.specialists[intent]
        specialist_result: AgentResult = specialist.run(request, {"intent": intent})
        action_items, action_trace = self.action_plan.build(specialist_result)

        response = FinalAIResponse(
            intent=intent,
            workflow=request.workflow,
            summary=specialist_result.summary,
            reasoning_summary=specialist_result.reasoning_summary,
            action_items=action_items,
            risks=specialist_result.risks,
            confidence=specialist_result.confidence,
            data_sources=specialist_result.data_sources,
            data_freshness=specialist_result.data_freshness,
            limitations=specialist_result.limitations.copy(),
            safety_flags=[],
            agent_trace=[router_trace, specialist_result.trace, action_trace],
            safety_disclaimer=EDUCATIONAL_DISCLAIMER,
        )
        return self.safety.review(request, response)


def map_to_legacy_intent(intent: AgentIntent) -> str:
    return {
        "portfolio": "portfolio",
        "market": "market",
        "life_planning": "retirement",
        "tax": "tax",
        "journal": "education",
        "education": "education",
        "safety": "safety",
    }[intent]
