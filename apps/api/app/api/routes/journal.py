from fastapi import APIRouter

from app.schemas.api import (
    DecisionJournalCreateRequest,
    DecisionJournalEntryResponse,
    DecisionJournalResponse,
)
from app.services.journal_service import create_journal_entry, list_journal_entries

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("/entries", response_model=DecisionJournalResponse)
def read_journal_entries() -> DecisionJournalResponse:
    return list_journal_entries()


@router.post("/entries", response_model=DecisionJournalEntryResponse)
def create_entry(request: DecisionJournalCreateRequest) -> DecisionJournalEntryResponse:
    return create_journal_entry(request)
