from fastapi import APIRouter

from app.schemas.api import WatchlistCreateRequest, WatchlistItemResponse, WatchlistResponse
from app.services.watchlist_service import create_watchlist_item, get_watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
def read_watchlist() -> WatchlistResponse:
    return get_watchlist()


@router.post("", response_model=WatchlistItemResponse)
def create_item(request: WatchlistCreateRequest) -> WatchlistItemResponse:
    return create_watchlist_item(request)
