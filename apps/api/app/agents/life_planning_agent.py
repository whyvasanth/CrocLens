from app.agents.base import BaseAgent, get_llm_adapter
from app.agents.schemas import AgentDataSource, AgentRequest, AgentResult, AgentTrace


class LifePlanningAgent(BaseAgent):
    agent_name = "life_planning"

    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        llm_note = get_llm_adapter().summarize("life_planning", request, "retirement debt emergency fund goals")
        return AgentResult(
            agent="life_planning",
            summary="Life planning connects retirement, debt, emergency cash, and major goals into one review.",
            reasoning_summary=(
                "Retirement and debt decisions affect flexibility, taxes, and long-term progress. "
                f"{llm_note}"
            ),
            action_items=[
                "Consider listing each debt with balance, APR, payment, and due date.",
                "Review employer match rules before changing retirement contributions.",
                "Compare emergency cash with near-term obligations.",
            ],
            risks=[
                "Changing debt payments or contributions can reduce flexibility.",
                "Retirement projections depend on assumptions and are not guarantees.",
            ],
            confidence="medium",
            data_sources=[
                AgentDataSource(
                    provider="croclens_sample_life_plan",
                    label="Sample retirement and debt context",
                    freshness="sample",
                    as_of="2026-05-05",
                    limitations=["Sample retirement and debt data only."],
                )
            ],
            data_freshness="sample",
            limitations=["This is educational planning context, not personalized financial advice."],
            trace=AgentTrace(
                agent="life_planning",
                status="used",
                input_summary="Retirement, debt, emergency fund, and goal context.",
                output_summary="Generated life planning review.",
                tools_used=["retirement_plan", "liability_summary"],
            ),
        )
