from app.agents.base import BaseAgent, get_llm_adapter
from app.agents.schemas import AgentDataSource, AgentRequest, AgentResult, AgentTrace
from app.data_providers import get_data_provider_registry


class MarketResearchAgent(BaseAgent):
    agent_name = "market_research"

    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        registry = get_data_provider_registry()
        data_sources: list[AgentDataSource] = []
        limitations = ["Market context may be sample fallback when live providers are unavailable."]
        tools_used: list[str] = []

        if request.asset_symbol:
            price = registry.get_market_price(request.asset_symbol)
            data_sources.append(
                AgentDataSource(
                    provider=price.provider,
                    label=f"{price.symbol_or_series_id} market price",
                    freshness=price.freshness,
                    as_of=price.as_of.isoformat(),
                    limitations=price.limitations,
                )
            )
            limitations.extend(price.limitations)
            tools_used.append("get_market_price")
            summary = f"{price.symbol_or_series_id} is shown at {price.value:,.2f} {price.currency or ''}."
        else:
            crypto = registry.get_crypto_price("bitcoin")
            data_sources.append(
                AgentDataSource(
                    provider=crypto.provider,
                    label="Bitcoin sample/public price context",
                    freshness=crypto.freshness,
                    as_of=crypto.as_of.isoformat(),
                    limitations=crypto.limitations,
                )
            )
            limitations.extend(crypto.limitations)
            tools_used.append("get_crypto_price")
            summary = "Market research context is available, with sample fallback if live providers are unavailable."

        llm_note = get_llm_adapter().summarize("market_research", request, summary)
        return AgentResult(
            agent="market_research",
            summary=summary,
            reasoning_summary=(
                "Market research uses allowlisted provider tools and treats prices as context, not instructions. "
                f"{llm_note}"
            ),
            action_items=[
                "Consider checking source freshness before using market context.",
                "Research whether the asset meaningfully affects your overall allocation.",
                "Compare short-term movement with your long-term goal before reacting.",
            ],
            risks=[
                "Provider data can be delayed, rate-limited, revised, or unavailable.",
                "Market movement does not automatically mean you should change your plan.",
            ],
            confidence="medium",
            data_sources=data_sources,
            data_freshness=data_sources[0].freshness if data_sources else "unknown",
            limitations=limitations,
            trace=AgentTrace(
                agent="market_research",
                status="used",
                input_summary="Market, stock, ETF, crypto, or macro context.",
                output_summary="Generated market research context with provider limitations.",
                tools_used=tools_used,
            ),
        )
