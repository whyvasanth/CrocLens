from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import AssetDetailCard, AssetDetailResponse, AssetResponse
from app.services.mock_data import (
    get_asset_by_id,
    get_asset_detail_by_id,
    list_asset_detail_cards,
    list_assets,
)
from app.services.portfolio_service import list_user_assets

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
def read_assets(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> list[AssetResponse]:
    if current_user is not None:
        return list_user_assets(db, current_user)

    return list_assets()


@router.get("/detail-cards", response_model=list[AssetDetailCard])
def read_asset_detail_cards() -> list[AssetDetailCard]:
    return list_asset_detail_cards()


@router.get("/{asset_id}/detail", response_model=AssetDetailResponse)
def read_asset_detail(asset_id: str) -> AssetDetailResponse:
    detail = get_asset_detail_by_id(asset_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset detail '{asset_id}' was not found.",
        )

    return detail


@router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(asset_id: str) -> AssetResponse:
    asset = get_asset_by_id(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' was not found.",
        )

    return asset
