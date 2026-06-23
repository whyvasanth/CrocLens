from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import ActionPlan, DecisionJournalEntry, Holding, Liability, Portfolio, User, WatchlistItem
from app.schemas.api import (
    DataExportResponse,
    DeleteDataResponse,
    PrivacySettingsRequest,
    PrivacySettingsResponse,
    SecurityStatusResponse,
    SourceMetadata,
)

SECURITY_SOURCE = SourceMetadata(
    name="CrocLens security configuration",
    freshness="Local MVP security settings",
    as_of="2026-05-06",
)

DEFAULT_PRIVACY_SETTINGS = PrivacySettingsRequest()


def get_security_status() -> SecurityStatusResponse:
    return SecurityStatusResponse(
        api_version=settings.api_version,
        authentication_status=(
            f"AUTH_MODE={settings.auth_mode}; local auth is "
            f"{'enabled for development' if settings.is_local_auth_enabled else 'disabled'}."
        ),
        rate_limit_per_minute=settings.rate_limit_per_minute,
        security_headers_enabled=[
            "X-CrocLens-Request-Id",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy",
        ],
        cors_origins=settings.cors_origins,
        logging_summary=(
            "Structured JSON request logs include timestamp, request ID, path, method, status code, duration, "
            "user ID when available, and error category. Passwords, tokens, cookies, and full financial payloads "
            "must not be logged."
        ),
        prompt_injection_guardrails=[
            "Detect direct trading instructions and guaranteed-return language.",
            "Detect attempts to ignore system or developer instructions.",
            "Keep financial safety rules outside user-controlled text.",
        ],
        data_rights=["Export data preview", "Delete data preview", "Privacy setting controls"],
    )


def get_privacy_settings(user: User | None = None) -> PrivacySettingsResponse:
    if user is None or user.profile is None:
        return _privacy_response(DEFAULT_PRIVACY_SETTINGS)

    return PrivacySettingsResponse(
        profile_id=user.profile.id,
        beginner_mode_enabled=user.profile.beginner_mode,
        store_assistant_history=user.profile.store_assistant_history,
        allow_product_analytics=user.profile.allow_product_analytics,
        allow_external_integrations=user.profile.allow_external_integrations,
        data_retention_days=user.profile.data_retention_days,
        explanation="These privacy settings are saved to your CrocLens profile.",
        updated_at=datetime.now(tz=UTC).isoformat(),
    )


def update_privacy_settings(request: PrivacySettingsRequest, user: User | None = None) -> PrivacySettingsResponse:
    if user is None or user.profile is None:
        return _privacy_response(request)

    user.profile.beginner_mode = request.beginner_mode_enabled
    user.profile.store_assistant_history = request.store_assistant_history
    user.profile.allow_product_analytics = request.allow_product_analytics
    user.profile.allow_external_integrations = request.allow_external_integrations
    user.profile.data_retention_days = request.data_retention_days
    return get_privacy_settings(user)


def build_data_export(db: Session | None = None, user: User | None = None) -> DataExportResponse:
    counts = _sample_record_counts() if db is None or user is None else _user_record_counts(db, user)
    return DataExportResponse(
        export_id=f"export_{uuid4().hex[:12]}",
        generated_at=datetime.now(tz=UTC).isoformat(),
        sections=[
            "profile",
            "portfolio_summary",
            "assets",
            "journal_entries",
            "watchlist_items",
            "privacy_settings",
        ],
        record_counts=counts,
        delivery_note="MVP preview only. Production should generate a downloadable JSON or CSV archive.",
        data_limitations=[
            "Export is a preview count, not a downloadable archive yet.",
            "Production exports should require confirmation and background archive generation.",
        ],
        sources=[SECURITY_SOURCE],
    )


def preview_delete_data() -> DeleteDataResponse:
    return DeleteDataResponse(
        request_id=f"delete_preview_{uuid4().hex[:12]}",
        status="preview_only",
        deleted_sections=[
            "profile",
            "manual_assets",
            "journal_entries",
            "watchlist_items",
            "assistant_history",
        ],
        explanation=(
            "This MVP endpoint previews what deletion would cover. Production deletion should require authentication, "
            "confirmation, audit logging, and background cleanup jobs."
        ),
        data_limitations=[
            "No persistent user data is deleted because the MVP still uses sample data.",
            "Production deletion must include database rows, object storage, logs where legally allowed, and AI history.",
        ],
    )


def _privacy_response(settings_request: PrivacySettingsRequest) -> PrivacySettingsResponse:
    return PrivacySettingsResponse(
        profile_id="sample_user_maya",
        beginner_mode_enabled=settings_request.beginner_mode_enabled,
        store_assistant_history=settings_request.store_assistant_history,
        allow_product_analytics=settings_request.allow_product_analytics,
        allow_external_integrations=settings_request.allow_external_integrations,
        data_retention_days=settings_request.data_retention_days,
        explanation=(
            "These controls are MVP previews. Production settings should be persisted per authenticated user."
        ),
        updated_at=datetime.now(tz=UTC).isoformat(),
    )


def _sample_record_counts() -> dict[str, int]:
    return {
        "profile": 1,
        "portfolio_summary": 1,
        "assets": 6,
        "journal_entries": 2,
        "watchlist_items": 2,
        "privacy_settings": 1,
    }


def _user_record_counts(db: Session, user: User) -> dict[str, int]:
    portfolio_ids = select(Portfolio.id).where(Portfolio.user_id == user.id)
    holding_count = _count(db, select(func.count(Holding.id)).where(Holding.portfolio_id.in_(portfolio_ids)))
    return {
        "profile": 1 if user.profile is not None else 0,
        "portfolio_summary": 1,
        "assets": holding_count,
        "holdings": holding_count,
        "liabilities": _count(db, select(func.count(Liability.id)).where(Liability.user_id == user.id)),
        "journal_entries": _count(db, select(func.count(DecisionJournalEntry.id)).where(DecisionJournalEntry.user_id == user.id)),
        "watchlist_items": _count(db, select(func.count(WatchlistItem.id)).where(WatchlistItem.user_id == user.id)),
        "action_plans": _count(db, select(func.count(ActionPlan.id)).where(ActionPlan.user_id == user.id)),
        "privacy_settings": 1,
    }


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)
