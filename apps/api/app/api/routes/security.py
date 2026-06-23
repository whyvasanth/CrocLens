from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user
from app.db.session import get_db
from app.models import User
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
def read_privacy_settings(current_user: User | None = Depends(get_optional_user)) -> PrivacySettingsResponse:
    return get_privacy_settings(current_user)


@router.put("/privacy/settings", response_model=PrivacySettingsResponse)
def update_settings(
    request: PrivacySettingsRequest,
    current_user: User | None = Depends(get_optional_user),
) -> PrivacySettingsResponse:
    return update_privacy_settings(request, current_user)


@router.get("/privacy/export", response_model=DataExportResponse)
def export_data(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> DataExportResponse:
    return build_data_export(db, current_user)


@router.delete("/privacy/data", response_model=DeleteDataResponse)
def delete_data_preview() -> DeleteDataResponse:
    return preview_delete_data()
