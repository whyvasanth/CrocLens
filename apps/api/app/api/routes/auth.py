from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies import require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import AccountCreateRequest, AccountLoginRequest, AccountSessionResponse, AccountUserResponse, LogoutResponse
from app.services.account_service import build_account_user_response, create_account, login_account, revoke_session_token

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/signup", response_model=AccountSessionResponse)
def signup(request: AccountCreateRequest, db: Session = Depends(get_db)) -> AccountSessionResponse:
    return create_account(request, db)


@router.post("/login", response_model=AccountSessionResponse)
def login(request: AccountLoginRequest, db: Session = Depends(get_db)) -> AccountSessionResponse:
    return login_account(request, db)


@router.get("/me", response_model=AccountUserResponse)
def read_current_user(current_user: User = Depends(require_current_user)) -> AccountUserResponse:
    return build_account_user_response(current_user)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> LogoutResponse:
    if credentials is not None:
        revoke_session_token(credentials.credentials, db)

    return LogoutResponse(status="logged_out")
