from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import settings
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
        authentication_status="Planned: verified free authentication later; MVP uses sample data only.",
        rate_limit_per_minute=settings.rate_limit_per_minute,
        security_headers_enabled=[
            "X-CrocLens-Request-Id",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy",
        ],
        cors_origins=settings.cors_origins,
        logging_summary="Request IDs, status codes, paths, and latency are logged; secrets and account numbers should not be logged.",
        prompt_injection_guardrails=[
            "Detect direct trading instructions and guaranteed-return language.",
            "Detect attempts to ignore system or developer instructions.",
            "Keep financial safety rules outside user-controlled text.",
        ],
        data_rights=["Export data preview", "Delete data preview", "Privacy setting controls"],
    )


def get_privacy_settings() -> PrivacySettingsResponse:
    return _privacy_response(DEFAULT_PRIVACY_SETTINGS)


def update_privacy_settings(request: PrivacySettingsRequest) -> PrivacySettingsResponse:
    return _privacy_response(request)


def build_data_export() -> DataExportResponse:
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
        record_counts={
            "profile": 1,
            "portfolio_summary": 1,
            "assets": 6,
            "journal_entries": 2,
            "watchlist_items": 2,
            "privacy_settings": 1,
        },
        delivery_note="MVP preview only. Production should generate a downloadable JSON or CSV archive.",
        data_limitations=[
            "No real user database is connected yet.",
            "Export contains sample record counts, not real financial data.",
            "Production exports should require authentication and user confirmation.",
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
