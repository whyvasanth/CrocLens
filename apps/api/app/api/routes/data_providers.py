from fastapi import APIRouter

from app.data_providers import get_data_provider_registry
from app.data_providers.schemas import DataFreshnessResponse, ProviderStatus

router = APIRouter(prefix="/data", tags=["data providers"])


@router.get("/providers", response_model=list[ProviderStatus])
def read_data_providers() -> list[ProviderStatus]:
    return get_data_provider_registry().list_provider_statuses()


@router.get("/freshness", response_model=DataFreshnessResponse)
def read_data_freshness() -> DataFreshnessResponse:
    return get_data_provider_registry().freshness()
