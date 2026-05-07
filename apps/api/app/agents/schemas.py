from typing import Literal

from pydantic import BaseModel, Field


AgentName = Literal[
    "router_agent",
    "wealth_analyst",
    "market_research",
    "life_planning",
    "tax_awareness",
    "action_plan",
    "decision_journal",
    "safety_guardrail",
]
AgentIntent = Literal["portfolio", "market", "life_planning", "tax", "journal", "education", "safety"]
AgentWorkflow = Literal["chat", "action_plan", "explain_asset", "portfolio_review"]
AgentRunStatus = Literal["used", "skipped"]
LLMMode = Literal["mock", "openai", "local_future"]


class AgentRequest(BaseModel):
    question: str = Field(min_length=2, max_length=800)
    workflow: AgentWorkflow = "chat"
    beginner_mode: bool = True
    asset_symbol: str | None = Field(default=None, max_length=32)


class AgentDataSource(BaseModel):
    provider: str
    label: str
    freshness: str
    as_of: str | None = None
    limitations: list[str] = Field(default_factory=list)


class AgentTrace(BaseModel):
    agent: AgentName
    status: AgentRunStatus
    input_summary: str
    output_summary: str
    tools_used: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    agent: AgentName
    summary: str
    reasoning_summary: str
    action_items: list[str]
    risks: list[str]
    confidence: Literal["low", "medium", "high"]
    data_sources: list[AgentDataSource]
    data_freshness: str
    limitations: list[str]
    trace: AgentTrace


class FinalAIResponse(BaseModel):
    intent: AgentIntent
    workflow: AgentWorkflow
    summary: str
    reasoning_summary: str
    action_items: list[str]
    risks: list[str]
    confidence: Literal["low", "medium", "high"]
    data_sources: list[AgentDataSource]
    data_freshness: str
    limitations: list[str]
    safety_flags: list[str]
    agent_trace: list[AgentTrace]
    safety_disclaimer: str
