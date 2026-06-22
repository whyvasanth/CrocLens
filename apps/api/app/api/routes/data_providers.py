from fastapi import APIRouter

from app.providers.models import ProviderStatusResponse
from app.providers.registry import build_default_provider_registry

router = APIRouter(prefix="/data-providers", tags=["data providers"])


@router.get("/status", response_model=ProviderStatusResponse)
async def read_data_provider_status() -> ProviderStatusResponse:
    registry = build_default_provider_registry()
    return await registry.status()
