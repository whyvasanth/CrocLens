from app.schemas.api import (
    AgentRegistryItem,
    AgentRegistryResponse,
    AgentRole,
    AgentTraceStep,
    AssistantIntent,
    AssistantSafetyCheck,
)

AGENT_REGISTRY: list[AgentRegistryItem] = [
    AgentRegistryItem(
        agent="intent_router",
        title="Intent Router Agent",
        purpose="Classifies the user question and chooses which specialist should handle it.",
        uses_tools=False,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="portfolio_analyst",
        title="Portfolio Analyst Agent",
        purpose="Explains net worth, allocation, diversification, and portfolio-level risk.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="cross_asset_comparison",
        title="Cross-Asset Comparison Agent",
        purpose="Compares stocks, ETFs, crypto, real estate, cash, bonds, retirement, and liabilities.",
        uses_tools=True,
        current_status="stubbed",
    ),
    AgentRegistryItem(
        agent="stock_etf_research",
        title="Stock/ETF Research Agent",
        purpose="Explains public market securities in beginner-friendly language.",
        uses_tools=True,
        current_status="stubbed",
    ),
    AgentRegistryItem(
        agent="crypto_research",
        title="Crypto Research Agent",
        purpose="Explains crypto volatility, custody, liquidity, and tax recordkeeping.",
        uses_tools=True,
        current_status="stubbed",
    ),
    AgentRegistryItem(
        agent="real_estate_insight",
        title="Real Estate Insight Agent",
        purpose="Explains property equity, mortgage context, and real estate concentration risk.",
        uses_tools=True,
        current_status="stubbed",
    ),
    AgentRegistryItem(
        agent="news_impact",
        title="News Impact Agent",
        purpose="Connects market or news events to user holdings and likely exposure.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="tax_aware",
        title="Tax-Aware Agent",
        purpose="Explains tax lots, holding periods, capital gains, and tax-loss harvesting concepts.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="retirement_planner",
        title="Retirement Planner Agent",
        purpose="Explains retirement accounts, contribution rates, employer match, and scenario assumptions.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="debt_liability_coach",
        title="Debt/Liability Coach Agent",
        purpose="Explains balances, rates, payoff tradeoffs, and debt impact on net worth.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="action_plan",
        title="Action Plan Agent",
        purpose="Turns an explanation into safe beginner next steps.",
        uses_tools=False,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="decision_journal_feedback",
        title="Decision Journal Feedback Agent",
        purpose="Reviews past decisions and compares expected versus actual outcomes.",
        uses_tools=True,
        current_status="stubbed",
    ),
    AgentRegistryItem(
        agent="safety_compliance_guardrail",
        title="Safety/Compliance Guardrail Agent",
        purpose="Checks output for direct advice, guaranteed returns, missing limitations, and unsafe wording.",
        uses_tools=False,
        current_status="implemented",
    ),
]

SPECIALIST_BY_INTENT: dict[AssistantIntent, AgentRole] = {
    "portfolio": "portfolio_analyst",
    "debt": "debt_liability_coach",
    "retirement": "retirement_planner",
    "tax": "tax_aware",
    "market": "news_impact",
    "risk": "cross_asset_comparison",
    "education": "portfolio_analyst",
    "safety": "safety_compliance_guardrail",
}

SPECIALIST_TOOLS: dict[AgentRole, list[str]] = {
    "portfolio_analyst": ["portfolio_summary"],
    "cross_asset_comparison": ["asset_allocation", "asset_scores"],
    "news_impact": ["market_snapshot_stub", "portfolio_summary"],
    "tax_aware": ["tax_lot_stub"],
    "retirement_planner": ["retirement_account_stub"],
    "debt_liability_coach": ["liability_summary"],
    "safety_compliance_guardrail": ["unsafe_language_rules"],
}


def get_agent_registry() -> AgentRegistryResponse:
    return AgentRegistryResponse(
        agents=AGENT_REGISTRY,
        orchestration_note=(
            "Phase 10 uses a lightweight deterministic orchestrator. Later phases can replace the "
            "step functions with LangGraph nodes or model calls while keeping the same trace contract."
        ),
    )


def get_agent_title(agent: AgentRole) -> str:
    return next(item.title for item in AGENT_REGISTRY if item.agent == agent)


def build_agent_trace(
    *,
    intent: AssistantIntent,
    question: str,
    answer_summary: str,
    safety: AssistantSafetyCheck,
) -> list[AgentTraceStep]:
    trace = [
        AgentTraceStep(
            agent="intent_router",
            title=get_agent_title("intent_router"),
            status="used",
            input_summary="User question was classified without returning raw prompt text.",
            output_summary=f"Routed request to the {intent} path.",
            tools_used=[],
        )
    ]

    specialist = SPECIALIST_BY_INTENT[intent]
    if specialist != "safety_compliance_guardrail":
        trace.append(
            AgentTraceStep(
                agent=specialist,
                title=get_agent_title(specialist),
                status="used",
                input_summary=f"Intent: {intent}",
                output_summary=answer_summary,
                tools_used=SPECIALIST_TOOLS.get(specialist, []),
            )
        )

        trace.append(
            AgentTraceStep(
                agent="action_plan",
                title=get_agent_title("action_plan"),
                status="used",
                input_summary="Specialist explanation and beginner mode output.",
                output_summary="Converted the explanation into safe next-step language.",
                tools_used=[],
            )
        )

    trace.append(
        AgentTraceStep(
            agent="safety_compliance_guardrail",
            title=get_agent_title("safety_compliance_guardrail"),
            status="used",
            input_summary="Draft assistant response and user question.",
            output_summary=(
                "Passed safety review."
                if safety.passed
                else "Reframed unsafe trading or guaranteed-return wording into educational language."
            ),
            tools_used=SPECIALIST_TOOLS["safety_compliance_guardrail"],
        )
    )

    return trace
