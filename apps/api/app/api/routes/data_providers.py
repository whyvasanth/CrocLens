from fastapi import APIRouter, Depends

from app.api.dependencies import get_provider_registry
from app.providers.models import ProviderStatusResponse
from app.providers.registry import ProviderRegistry

router = APIRouter(prefix="/data-providers", tags=["data providers"])


@router.get("/status", response_model=ProviderStatusResponse)
async def read_data_provider_status(
    registry: ProviderRegistry = Depends(get_provider_registry),
) -> ProviderStatusResponse:
    return await registry.status()
