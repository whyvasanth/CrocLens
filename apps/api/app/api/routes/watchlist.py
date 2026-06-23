from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import DeleteRecordResponse, WatchlistCreateRequest, WatchlistItemResponse, WatchlistResponse, WatchlistUpdateRequest
from app.services.watchlist_service import create_watchlist_item, delete_watchlist_item, get_watchlist, update_watchlist_item

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
def read_watchlist(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> WatchlistResponse:
    return get_watchlist(db, current_user)


@router.post("", response_model=WatchlistItemResponse)
def create_item(
    request: WatchlistCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> WatchlistItemResponse:
    return create_watchlist_item(request, db, current_user)


@router.put("/{item_id}", response_model=WatchlistItemResponse)
def update_item(
    item_id: str,
    request: WatchlistUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> WatchlistItemResponse:
    return update_watchlist_item(db, current_user, item_id, request)


@router.delete("/{item_id}", response_model=DeleteRecordResponse)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_watchlist_item(db, current_user, item_id)
