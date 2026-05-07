from app.agents.base import BaseAgent, get_llm_adapter
from app.agents.schemas import AgentDataSource, AgentRequest, AgentResult, AgentTrace
from app.services.mock_data import get_portfolio_summary


class WealthAnalystAgent(BaseAgent):
    agent_name = "wealth_analyst"

    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        portfolio = get_portfolio_summary()
        llm_note = get_llm_adapter().summarize("wealth_analyst", request, "portfolio sample context")
        return AgentResult(
            agent="wealth_analyst",
            summary=(
                f"Your sample net worth is ${portfolio.net_worth:,.0f}, with "
                f"${portfolio.total_assets:,.0f} in assets and ${portfolio.total_liabilities:,.0f} in liabilities."
            ),
            reasoning_summary=(
                "The wealth review combines assets, liabilities, allocation, liquidity, diversification, and risk. "
                f"{llm_note}"
            ),
            action_items=[
                "Consider reviewing whether your largest asset classes match your time horizon.",
                "Compare liquid cash with near-term debts and emergency needs.",
                "Review concentration risk before focusing on any single holding.",
            ],
            risks=[
                "Sample data may not match real account balances.",
                "Net worth can change quickly when market prices, home values, or debt balances change.",
            ],
            confidence="medium",
            data_sources=[
                AgentDataSource(
                    provider="croclens_sample_portfolio",
                    label="Sample portfolio summary",
                    freshness="sample",
                    as_of="2026-05-05",
                    limitations=["Sample portfolio data only."],
                )
            ],
            data_freshness="sample",
            limitations=["This is educational and uses sample CrocLens data, not connected financial accounts."],
            trace=AgentTrace(
                agent="wealth_analyst",
                status="used",
                input_summary="Portfolio and whole-wealth context.",
                output_summary="Generated whole-wealth review.",
                tools_used=["portfolio_summary", "asset_allocation", "asset_scores"],
            ),
        )
