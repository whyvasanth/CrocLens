from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import AgentRegistryResponse, AssistantRequest, AssistantResponse
from app.services.agent_orchestrator import get_agent_registry
from app.services.assistant_service import answer_question

router = APIRouter(prefix="/ai", tags=["ai assistant"])


@router.post("/assistant", response_model=AssistantResponse)
def ask_assistant(
    request: AssistantRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> AssistantResponse:
    return answer_question(request, db=db, current_user=current_user)


@router.get("/agents", response_model=AgentRegistryResponse)
def read_agent_registry() -> AgentRegistryResponse:
    return get_agent_registry()
