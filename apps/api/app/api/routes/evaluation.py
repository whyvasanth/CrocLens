from fastapi import APIRouter

from app.schemas.api import EvaluationMetricsResponse
from app.services.evaluation_service import get_evaluation_metrics

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/metrics", response_model=EvaluationMetricsResponse)
def read_evaluation_metrics() -> EvaluationMetricsResponse:
    return get_evaluation_metrics()
