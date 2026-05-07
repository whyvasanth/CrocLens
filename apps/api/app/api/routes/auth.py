from fastapi import APIRouter

from app.schemas.api import AccountCreateRequest, AccountLoginRequest, AccountSessionResponse
from app.services.account_service import create_account, login_account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AccountSessionResponse)
def signup(request: AccountCreateRequest) -> AccountSessionResponse:
    return create_account(request)


@router.post("/login", response_model=AccountSessionResponse)
def login(request: AccountLoginRequest) -> AccountSessionResponse:
    return login_account(request)
