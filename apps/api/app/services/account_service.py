from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.api import (
    AccountCreateRequest,
    AccountLoginRequest,
    AccountSessionResponse,
    AccountUserResponse,
    SourceMetadata,
)
from app.services.onboarding_service import create_onboarding_profile

ACCOUNT_SOURCE = SourceMetadata(
    name="CrocLens mock account service",
    freshness="Local deterministic MVP auth preview",
    as_of="2026-05-07",
)

SECURITY_NOTE = (
    "MVP account endpoints are local mock flows only. Production auth must hash passwords, persist users, "
    "protect sessions, verify email, and add recovery controls."
)


def create_account(request: AccountCreateRequest) -> AccountSessionResponse:
    onboarding_profile = create_onboarding_profile(request.onboarding_profile)
    user = AccountUserResponse(
        id=f"user_{uuid4().hex[:12]}",
        display_name=request.display_name.strip(),
        email=request.email.strip().lower(),
        beginner_mode_enabled=True,
        created_at=datetime.now(tz=UTC).isoformat(),
    )

    return AccountSessionResponse(
        user=user,
        onboarding_profile=onboarding_profile,
        session_token=f"mock_session_{uuid4().hex}",
        token_type="mock_session",
        expires_in_minutes=60,
        next_path="/dashboard",
        confidence="medium",
        data_limitations=[
            "This MVP does not persist accounts yet.",
            "Passwords are accepted only to model the API contract; production must hash and store credentials safely.",
            "The session token is a mock value and should not be used as real authentication.",
        ],
        sources=[ACCOUNT_SOURCE],
        security_note=SECURITY_NOTE,
    )


def login_account(request: AccountLoginRequest) -> AccountSessionResponse:
    user_name = request.email.split("@")[0].replace(".", " ").replace("_", " ").title() or "CrocLens User"
    user = AccountUserResponse(
        id="user_sample_login",
        display_name=user_name,
        email=request.email.strip().lower(),
        beginner_mode_enabled=True,
        created_at=datetime.now(tz=UTC).isoformat(),
    )

    return AccountSessionResponse(
        user=user,
        onboarding_profile=None,
        session_token=f"mock_session_{uuid4().hex}",
        token_type="mock_session",
        expires_in_minutes=60,
        next_path="/dashboard",
        confidence="low",
        data_limitations=[
            "Login is a local mock preview and does not verify a stored password yet.",
            "No account database or production session store is connected.",
            "Use this only for MVP navigation and API contract testing.",
        ],
        sources=[ACCOUNT_SOURCE],
        security_note=SECURITY_NOTE,
    )
