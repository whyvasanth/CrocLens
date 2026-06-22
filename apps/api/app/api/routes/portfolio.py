from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, get_provider_registry, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import (
    DeleteRecordResponse,
    HoldingCreateRequest,
    HoldingResponse,
    HoldingUpdateRequest,
    LiabilityCreateRequest,
    LiabilityResponse,
    LiabilityUpdateRequest,
    PortfolioHistoryResponse,
    PortfolioRefreshPricesResponse,
    PortfolioRecordsResponse,
    PortfolioSummaryResponse,
)
from app.providers.registry import ProviderRegistry
from app.services.mock_data import get_portfolio_summary
from app.services.portfolio_service import (
    create_holding,
    create_liability,
    delete_holding,
    delete_liability,
    get_portfolio_records,
    get_user_portfolio_summary,
    list_user_holdings,
    list_user_liabilities,
    update_holding,
    update_liability,
)
from app.services.market_api_service import get_portfolio_history_response, refresh_portfolio_prices_response

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=PortfolioSummaryResponse)
def read_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> PortfolioSummaryResponse:
    if current_user is not None:
        return get_user_portfolio_summary(db, current_user)

    return get_portfolio_summary()


@router.get("/records", response_model=PortfolioRecordsResponse)
def read_portfolio_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> PortfolioRecordsResponse:
    return get_portfolio_records(db, current_user)


@router.get("/history", response_model=PortfolioHistoryResponse)
def read_portfolio_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> PortfolioHistoryResponse:
    return get_portfolio_history_response(db, current_user)


@router.post("/refresh-prices", response_model=PortfolioRefreshPricesResponse)
async def refresh_portfolio_prices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
    registry: ProviderRegistry = Depends(get_provider_registry),
) -> PortfolioRefreshPricesResponse:
    return await refresh_portfolio_prices_response(db, registry, current_user)


@router.get("/holdings", response_model=list[HoldingResponse])
def read_holdings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> list[HoldingResponse]:
    return list_user_holdings(db, current_user)


@router.post("/holdings", response_model=HoldingResponse)
def add_holding(
    request: HoldingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> HoldingResponse:
    return create_holding(db, current_user, request)


@router.put("/holdings/{holding_id}", response_model=HoldingResponse)
def edit_holding(
    holding_id: str,
    request: HoldingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> HoldingResponse:
    return update_holding(db, current_user, holding_id, request)


@router.delete("/holdings/{holding_id}", response_model=DeleteRecordResponse)
def remove_holding(
    holding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_holding(db, current_user, holding_id)


@router.get("/liabilities", response_model=list[LiabilityResponse])
def read_liabilities(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> list[LiabilityResponse]:
    return list_user_liabilities(db, current_user)


@router.post("/liabilities", response_model=LiabilityResponse)
def add_liability(
    request: LiabilityCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> LiabilityResponse:
    return create_liability(db, current_user, request)


@router.put("/liabilities/{liability_id}", response_model=LiabilityResponse)
def edit_liability(
    liability_id: str,
    request: LiabilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> LiabilityResponse:
    return update_liability(db, current_user, liability_id, request)


@router.delete("/liabilities/{liability_id}", response_model=DeleteRecordResponse)
def remove_liability(
    liability_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_liability(db, current_user, liability_id)
