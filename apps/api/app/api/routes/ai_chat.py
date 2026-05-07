from fastapi import APIRouter

from app.agents.orchestrator import CrocLensAgentOrchestrator
from app.agents.schemas import AgentRequest, FinalAIResponse

router = APIRouter(prefix="/ai", tags=["ai agents"])


@router.post("/chat", response_model=FinalAIResponse)
def chat_with_croc_guide(request: AgentRequest) -> FinalAIResponse:
    return CrocLensAgentOrchestrator().run(request)


@router.post("/action-plan", response_model=FinalAIResponse)
def generate_ai_action_plan(request: AgentRequest) -> FinalAIResponse:
    return CrocLensAgentOrchestrator().run(request.model_copy(update={"workflow": "action_plan"}))


@router.post("/explain-asset", response_model=FinalAIResponse)
def explain_asset(request: AgentRequest) -> FinalAIResponse:
    return CrocLensAgentOrchestrator().run(request.model_copy(update={"workflow": "explain_asset"}))


@router.post("/portfolio-review", response_model=FinalAIResponse)
def review_portfolio(request: AgentRequest) -> FinalAIResponse:
    return CrocLensAgentOrchestrator().run(request.model_copy(update={"workflow": "portfolio_review"}))
