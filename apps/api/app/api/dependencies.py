from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.providers.registry import ProviderRegistry, build_default_provider_registry
from app.services.account_service import get_user_for_session_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None

    user = get_user_for_session_token(credentials.credentials, db)
    if user is not None:
        request.state.user_id = user.id
    return user


def require_current_user(current_user: User | None = Depends(get_current_user)) -> User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    return current_user


def get_optional_user(current_user: User | None = Depends(get_current_user)) -> User | None:
    return current_user


def get_provider_registry() -> ProviderRegistry:
    return build_default_provider_registry()
