from app.schemas.api import AssistantRequest, AssistantResponse
from app.services.mock_data import EDUCATIONAL_DISCLAIMER, MOCK_SOURCE


def answer_question(request: AssistantRequest) -> AssistantResponse:
    question = request.question.strip()

    return AssistantResponse(
        summary="Croc Guide can help explain this using your sample dashboard data.",
        beginner_explanation=(
            "Based on the data provided, the biggest beginner-friendly idea is to compare risk, "
            "liquidity, debt, and diversification together instead of looking at one asset alone."
        ),
        suggested_next_steps=[
            "Consider reviewing your asset allocation before focusing on any single holding.",
            "You may want to research how higher-interest debt affects net worth.",
            "Check the data freshness label before relying on any market movement.",
        ],
        confidence="medium",
        data_limitations=[
            "Question received: " + question,
            "This response uses mock Phase 3 data, not live financial accounts.",
            "No real market data, tax lots, or user-specific legal context is connected yet.",
        ],
        sources=[MOCK_SOURCE],
        safety_disclaimer=EDUCATIONAL_DISCLAIMER,
    )

