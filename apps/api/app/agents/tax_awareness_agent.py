from app.agents.base import BaseAgent, get_llm_adapter
from app.agents.schemas import AgentDataSource, AgentRequest, AgentResult, AgentTrace


class TaxAwarenessAgent(BaseAgent):
    agent_name = "tax_awareness"

    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        llm_note = get_llm_adapter().summarize("tax_awareness", request, "tax lots wash sale holding period")
        return AgentResult(
            agent="tax_awareness",
            summary="Tax-aware context should focus on education, holding periods, cost basis, and wash-sale cautions.",
            reasoning_summary=(
                "Tax outputs are intentionally cautious because rules depend on account type, timing, income, and jurisdiction. "
                f"{llm_note}"
            ),
            action_items=[
                "Consider reviewing purchase dates and cost basis before selling taxable assets.",
                "Research short-term versus long-term holding period basics.",
                "Discuss specific tax decisions with a qualified tax professional.",
            ],
            risks=[
                "Tax lots may be incomplete or incorrect without brokerage data.",
                "Wash-sale rules and tax treatment can be complex.",
            ],
            confidence="medium",
            data_sources=[
                AgentDataSource(
                    provider="croclens_sample_tax_lots",
                    label="Sample tax lot context",
                    freshness="sample",
                    as_of="2026-05-05",
                    limitations=["Sample tax data only; not tax advice."],
                )
            ],
            data_freshness="sample",
            limitations=["This is educational tax context, not tax advice."],
            trace=AgentTrace(
                agent="tax_awareness",
                status="used",
                input_summary="Tax lot, holding period, and wash-sale context.",
                output_summary="Generated cautious tax-aware explanation.",
                tools_used=["tax_lot_summary"],
            ),
        )
