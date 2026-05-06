from fastapi import APIRouter

from app.schemas.api import (
    DataExportResponse,
    DeleteDataResponse,
    PrivacySettingsRequest,
    PrivacySettingsResponse,
    SecurityStatusResponse,
)
from app.services.security_service import (
    build_data_export,
    get_privacy_settings,
    get_security_status,
    preview_delete_data,
    update_privacy_settings,
)

router = APIRouter(tags=["security"])


@router.get("/security/status", response_model=SecurityStatusResponse)
def read_security_status() -> SecurityStatusResponse:
    return get_security_status()


@router.get("/privacy/settings", response_model=PrivacySettingsResponse)
def read_privacy_settings() -> PrivacySettingsResponse:
    return get_privacy_settings()


@router.put("/privacy/settings", response_model=PrivacySettingsResponse)
def update_settings(request: PrivacySettingsRequest) -> PrivacySettingsResponse:
    return update_privacy_settings(request)


@router.get("/privacy/export", response_model=DataExportResponse)
def export_data() -> DataExportResponse:
    return build_data_export()


@router.delete("/privacy/data", response_model=DeleteDataResponse)
def delete_data_preview() -> DeleteDataResponse:
    return preview_delete_data()
