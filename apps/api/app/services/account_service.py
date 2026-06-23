from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_session_token,
    hash_password,
    hash_session_token,
    utc_after_minutes,
    utc_now,
    verify_password,
)
from app.models import LocalAuthSession, Portfolio, User, UserProfile
from app.schemas.api import (
    AccountCreateRequest,
    AccountLoginRequest,
    AccountSessionResponse,
    AccountUserResponse,
    OnboardingProfileResponse,
    SourceMetadata,
)
from app.services.onboarding_service import create_onboarding_profile
from app.services.portfolio_service import create_manual_asset_holdings_for_user

LOCAL_SESSION_MINUTES = 60

ACCOUNT_SOURCE = SourceMetadata(
    name="CrocLens local account service",
    freshness="Persisted local development auth",
    as_of="2026-06-22",
)

SECURITY_NOTE = (
    "Local authentication is for development only. Production auth is designed to use Cognito with validated JWTs, "
    "secure cookies, email verification, password reset, and session expiration."
)

LOCAL_AUTH_DATABASE_NOT_READY_DETAIL = (
    "CrocLens account storage is not ready. Run database migrations, make sure PostgreSQL is running, "
    "then seed or create the local test user."
)


def create_account(request: AccountCreateRequest, db: Session) -> AccountSessionResponse:
    try:
        _require_local_auth()
        email = _normalize_email(request.email)
        display_name = request.display_name.strip()

        if _get_user_by_email(db, email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        onboarding_profile = create_onboarding_profile(request.onboarding_profile)
        user = User(
            id=str(uuid4()),
            email=email,
            full_name=display_name,
            status="active",
            auth_provider="local",
            password_hash=hash_password(request.password),
        )
        user.profile = UserProfile(
            id=str(uuid4()),
            beginner_mode=True,
            risk_tolerance=request.onboarding_profile.risk_tolerance,
            time_horizon=request.onboarding_profile.time_horizon,
            primary_goal=request.onboarding_profile.primary_goal,
            household_income_range=request.onboarding_profile.income_range,
        )
        user.portfolios.append(
            Portfolio(
                id=str(uuid4()),
                name="My CrocLens Portfolio",
                base_currency="USD",
            )
        )

        db.add(user)
        try:
            db.flush()
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            ) from exc

        create_manual_asset_holdings_for_user(db, user, request.onboarding_profile.manual_assets)

        return _build_session_response(
            db=db,
            user=user,
            onboarding_profile=onboarding_profile,
            confidence="high",
            data_limitations=[
                "Local auth persists users and hashed passwords for development.",
                "Production still needs Cognito authorization-code flow with PKCE and server-managed secure cookies.",
                "Manual assets from signup are stored as user-owned portfolio holdings.",
            ],
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise _local_auth_database_not_ready() from exc


def login_account(request: AccountLoginRequest, db: Session) -> AccountSessionResponse:
    try:
        _require_local_auth()
        email = _normalize_email(request.email)
        user = _get_user_by_email(db, email)

        if user is None or user.status != "active" or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        return _build_session_response(
            db=db,
            user=user,
            onboarding_profile=None,
            confidence="high",
            data_limitations=[
                "Password verification uses bcrypt for local development.",
                "This session is persisted locally and expires automatically.",
                "Production should replace this local session token with a Cognito-backed secure cookie flow.",
            ],
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise _local_auth_database_not_ready() from exc


def get_user_for_session_token(token: str, db: Session) -> User | None:
    token_hash = hash_session_token(token)
    session = db.scalar(
        select(LocalAuthSession)
        .where(LocalAuthSession.token_hash == token_hash)
        .where(LocalAuthSession.revoked_at.is_(None))
        .where(LocalAuthSession.expires_at > utc_now())
    )

    if session is None or session.user.status != "active":
        return None

    return session.user


def revoke_session_token(token: str, db: Session) -> None:
    token_hash = hash_session_token(token)
    session = db.scalar(
        select(LocalAuthSession)
        .where(LocalAuthSession.token_hash == token_hash)
        .where(LocalAuthSession.revoked_at.is_(None))
    )

    if session is not None:
        session.revoked_at = utc_now()
        db.add(session)


def build_account_user_response(user: User) -> AccountUserResponse:
    return AccountUserResponse(
        id=user.id,
        display_name=user.full_name or user.email.split("@")[0],
        email=user.email,
        beginner_mode_enabled=user.profile.beginner_mode if user.profile else True,
        created_at=user.created_at.isoformat(),
    )


def _build_session_response(
    db: Session,
    user: User,
    onboarding_profile: OnboardingProfileResponse | None,
    confidence: str,
    data_limitations: list[str],
) -> AccountSessionResponse:
    token = create_session_token()
    session = LocalAuthSession(
        id=str(uuid4()),
        user_id=user.id,
        token_hash=hash_session_token(token),
        expires_at=utc_after_minutes(LOCAL_SESSION_MINUTES),
    )
    db.add(session)
    db.flush()

    return AccountSessionResponse(
        user=build_account_user_response(user),
        onboarding_profile=onboarding_profile,
        session_token=token,
        token_type="local_session",
        expires_in_minutes=LOCAL_SESSION_MINUTES,
        next_path="/dashboard",
        confidence=confidence,
        data_limitations=data_limitations,
        sources=[ACCOUNT_SOURCE],
        security_note=SECURITY_NOTE,
    )


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email).where(User.auth_provider == "local"))


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _require_local_auth() -> None:
    if not settings.is_local_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local authentication is disabled for this environment.",
        )


def _local_auth_database_not_ready() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=LOCAL_AUTH_DATABASE_NOT_READY_DETAIL,
    )
