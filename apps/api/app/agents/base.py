from abc import ABC, abstractmethod

from app.core.config import settings
from app.agents.schemas import AgentRequest, AgentResult


class LLMAdapter(ABC):
    @abstractmethod
    def summarize(self, prompt_name: str, request: AgentRequest, context: str) -> str:
        raise NotImplementedError


class MockLLMAdapter(LLMAdapter):
    def summarize(self, prompt_name: str, request: AgentRequest, context: str) -> str:
        return (
            f"Mock LLM mode used {prompt_name}. "
            "CrocLens generated a deterministic educational response without a paid model call."
        )


class OpenAIPlaceholderAdapter(LLMAdapter):
    def summarize(self, prompt_name: str, request: AgentRequest, context: str) -> str:
        return (
            "OPENAI_API_KEY is configured, but Phase 21 keeps OpenAI calls disabled by default. "
            "This placeholder preserves the adapter boundary without making paid calls."
        )


def get_llm_adapter() -> LLMAdapter:
    if settings.llm_mode == "openai" and settings.openai_api_key:
        return OpenAIPlaceholderAdapter()
    return MockLLMAdapter()


class BaseAgent(ABC):
    agent_name: str

    @abstractmethod
    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        raise NotImplementedError
