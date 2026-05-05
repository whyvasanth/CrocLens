from fastapi import APIRouter

from app.schemas.api import AgentRegistryResponse, AssistantRequest, AssistantResponse
from app.services.agent_orchestrator import get_agent_registry
from app.services.assistant_service import answer_question

router = APIRouter(prefix="/ai", tags=["ai assistant"])


@router.post("/assistant", response_model=AssistantResponse)
def ask_assistant(request: AssistantRequest) -> AssistantResponse:
    return answer_question(request)


@router.get("/agents", response_model=AgentRegistryResponse)
def read_agent_registry() -> AgentRegistryResponse:
    return get_agent_registry()
