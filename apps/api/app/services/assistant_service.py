from app.agents.orchestrator import CrocLensAgentOrchestrator, map_to_legacy_intent
from app.agents.schemas import AgentRequest, FinalAIResponse
from app.schemas.api import (
    AgentTraceStep,
    AssistantPromptContext,
    AssistantRequest,
    AssistantResponse,
    AssistantSafetyCheck,
    SourceMetadata,
)
from app.services.agent_orchestrator import get_agent_title

PROMPT_VERSION = "assistant_v2_phase21_agent_architecture_2026_05_07"

SYSTEM_RULES = [
    "You are Croc Guide, a friendly educational finance assistant for beginners.",
    "Do not provide direct buy, sell, or hold instructions.",
    "Do not promise returns or use guaranteed language.",
    "Use safe wording such as consider reviewing, worth researching, and based on the data provided.",
    "Always include confidence, limitations, source freshness, and an educational disclaimer.",
    "Agents may only use allowlisted provider tools and the safety guardrail always runs last.",
]


def normalize_question(question: str) -> str:
    return " ".join(question.strip().split())


def answer_question(request: AssistantRequest) -> AssistantResponse:
    question = normalize_question(request.question)
    final = CrocLensAgentOrchestrator().run(
        AgentRequest(question=question, workflow="chat", beginner_mode=request.beginner_mode)
    )
    legacy_intent = map_to_legacy_intent(final.intent)
    safety = AssistantSafetyCheck(
        passed=not final.safety_flags,
        flags=final.safety_flags,
        rewritten_question=(
            "The request was reframed into educational review language."
            if final.safety_flags
            else None
        ),
    )

    return AssistantResponse(
        intent=legacy_intent,
        summary=final.summary,
        beginner_explanation=final.reasoning_summary,
        suggested_next_steps=final.action_items,
        confidence=final.confidence,
        data_limitations=final.limitations,
        sources=_map_sources(final),
        safety=safety,
        agent_trace=_map_trace(final),
        prompt_context=_build_prompt_context(question, legacy_intent, final) if request.include_prompt_debug else None,
        safety_disclaimer=final.safety_disclaimer,
    )


def _map_sources(final: FinalAIResponse) -> list[SourceMetadata]:
    if not final.data_sources:
        return [SourceMetadata(name="CrocLens sample context", freshness="sample", as_of=None)]

    return [
        SourceMetadata(
            name=f"{source.provider}: {source.label}",
            freshness=source.freshness,
            as_of=source.as_of,
        )
        for source in final.data_sources
    ]


def _map_trace(final: FinalAIResponse) -> list[AgentTraceStep]:
    return [
        AgentTraceStep(
            agent=step.agent,
            title=get_agent_title(step.agent),
            status=step.status,
            input_summary=step.input_summary,
            output_summary=step.output_summary,
            tools_used=step.tools_used,
        )
        for step in final.agent_trace
    ]


def _build_prompt_context(question: str, intent: str, final: FinalAIResponse) -> AssistantPromptContext:
    return AssistantPromptContext(
        prompt_version=PROMPT_VERSION,
        intent=intent,
        system_rules=SYSTEM_RULES,
        context_summary=(
            f"Workflow: {final.workflow}. Data freshness: {final.data_freshness}. "
            f"Sources: {', '.join(source.provider for source in final.data_sources) or 'sample'}."
        ),
        user_question=question,
    )
