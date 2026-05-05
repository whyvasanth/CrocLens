from fastapi import APIRouter

from app.schemas.api import AssistantRequest, AssistantResponse
from app.services.assistant_service import answer_question

router = APIRouter(prefix="/ai", tags=["ai assistant"])


@router.post("/assistant", response_model=AssistantResponse)
def ask_assistant(request: AssistantRequest) -> AssistantResponse:
    return answer_question(request)

