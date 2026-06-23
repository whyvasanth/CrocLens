from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_optional_user, require_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import (
    DecisionJournalCreateRequest,
    DecisionJournalEntryResponse,
    DecisionJournalResponse,
    DecisionJournalUpdateRequest,
    DeleteRecordResponse,
)
from app.services.journal_service import create_journal_entry, delete_journal_entry, list_journal_entries, update_journal_entry

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/entries", response_model=DecisionJournalResponse)
def read_journal_entries(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> DecisionJournalResponse:
    return list_journal_entries(db, current_user)


@router.post("/entries", response_model=DecisionJournalEntryResponse)
def create_entry(
    request: DecisionJournalCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> DecisionJournalEntryResponse:
    return create_journal_entry(request, db, current_user)


@router.put("/entries/{entry_id}", response_model=DecisionJournalEntryResponse)
def update_entry(
    entry_id: str,
    request: DecisionJournalUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DecisionJournalEntryResponse:
    return update_journal_entry(db, current_user, entry_id, request)


@router.delete("/entries/{entry_id}", response_model=DeleteRecordResponse)
def delete_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
) -> DeleteRecordResponse:
    return delete_journal_entry(db, current_user, entry_id)
