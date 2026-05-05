from fastapi import APIRouter, HTTPException, status

from app.schemas.api import AssetResponse
from app.services.mock_data import get_asset_by_id, list_assets

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
def read_assets() -> list[AssetResponse]:
    return list_assets()


@router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(asset_id: str) -> AssetResponse:
    asset = get_asset_by_id(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' was not found.",
        )

    return asset

