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
        agent="router_agent",
        title="Router Agent",
        purpose="Classifies the user request and selects the safest specialist workflow.",
        uses_tools=False,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="wealth_analyst",
        title="Wealth Analyst Agent",
        purpose="Handles portfolio, cross-asset allocation, net worth, liquidity, diversification, and risk.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="market_research",
        title="Market Research Agent",
        purpose="Handles stock, ETF, crypto, news, and macro context using allowlisted provider tools.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="life_planning",
        title="Life Planning Agent",
        purpose="Handles retirement, debt, emergency fund, and major financial goal context.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="tax_awareness",
        title="Tax Awareness Agent",
        purpose="Explains tax lots, holding periods, tax-loss harvesting concepts, and wash-sale warnings cautiously.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="action_plan",
        title="Action Plan Agent",
        purpose="Turns specialist findings into safe beginner-friendly next steps.",
        uses_tools=False,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="decision_journal",
        title="Decision Journal Agent",
        purpose="Reviews user decisions as a learning loop using reason, expected outcome, risk, and review date.",
        uses_tools=True,
        current_status="implemented",
    ),
    AgentRegistryItem(
        agent="safety_guardrail",
        title="Safety Guardrail Agent",
        purpose="Validates all outputs for unsafe advice, missing limitations, and missing disclaimers.",
        uses_tools=False,
        current_status="implemented",
    ),
]

SPECIALIST_BY_INTENT: dict[AssistantIntent, AgentRole] = {
    "portfolio": "wealth_analyst",
    "debt": "life_planning",
    "retirement": "life_planning",
    "tax": "tax_awareness",
    "market": "market_research",
    "risk": "wealth_analyst",
    "education": "wealth_analyst",
    "safety": "safety_guardrail",
}


def get_agent_registry() -> AgentRegistryResponse:
    return AgentRegistryResponse(
        agents=AGENT_REGISTRY,
        orchestration_note=(
            "Phase 21 consolidates the previous 13 conceptual agents into 8 efficient LLM-ready agents. "
            "The default runtime remains deterministic mock mode and always runs the safety guardrail last."
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
            agent="router_agent",
            title=get_agent_title("router_agent"),
            status="used",
            input_summary=f"Question: {question}",
            output_summary=f"Routed request to the {intent} path.",
            tools_used=[],
        )
    ]

    specialist = SPECIALIST_BY_INTENT[intent]
    if specialist != "safety_guardrail":
        trace.append(
            AgentTraceStep(
                agent=specialist,
                title=get_agent_title(specialist),
                status="used",
                input_summary=f"Intent: {intent}",
                output_summary=answer_summary,
                tools_used=["allowlisted_provider_tools"] if specialist == "market_research" else ["sample_context"],
            )
        )

        trace.append(
            AgentTraceStep(
                agent="action_plan",
                title=get_agent_title("action_plan"),
                status="used",
                input_summary="Specialist output.",
                output_summary="Converted explanation into safe next-step language.",
                tools_used=[],
            )
        )

    trace.append(
        AgentTraceStep(
            agent="safety_guardrail",
            title=get_agent_title("safety_guardrail"),
            status="used",
            input_summary="Draft assistant response and user question.",
            output_summary="Passed safety review." if safety.passed else "Reframed unsafe wording into educational language.",
            tools_used=["unsafe_language_rules", "prompt_injection_rules"],
        )
    )

    return trace
