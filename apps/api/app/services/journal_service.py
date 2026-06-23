from datetime import UTC, date, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DecisionJournalEntry, User
from app.schemas.api import (
    DecisionJournalCreateRequest,
    DecisionJournalEntryResponse,
    DecisionJournalResponse,
    DecisionJournalUpdateRequest,
    DeleteRecordResponse,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


JOURNAL_SOURCE = SourceMetadata(
    name="CrocLens sample decision journal",
    freshness="Sample journal entries",
    as_of="2026-05-06",
)

PERSISTED_JOURNAL_SOURCE = SourceMetadata(
    name="CrocLens decision journal records",
    freshness="Saved user journal entries",
    as_of=date.today().isoformat(),
)


def list_journal_entries(db: Session | None = None, user: User | None = None) -> DecisionJournalResponse:
    if db is None or user is None:
        return _sample_journal()

    entries = list(
        db.scalars(
            select(DecisionJournalEntry)
            .where(DecisionJournalEntry.user_id == user.id)
            .order_by(DecisionJournalEntry.created_at.desc())
        )
    )

    return DecisionJournalResponse(
        entries=[_build_entry_response(entry) for entry in entries],
        feedback_prompts=[
            "Did the decision match the reason recorded at the time?",
            "Was the risk considered specific enough?",
            "What would you change about the decision process next time?",
        ],
        beginner_summary=(
            "Your decision journal helps you learn from your reasoning instead of judging every choice only by short-term results."
        ),
        confidence="medium",
        data_limitations=[
            "Journal entries are saved to your account.",
            "Feedback is deterministic and educational.",
            "CrocLens does not evaluate whether a financial decision was objectively right or wrong.",
        ],
        sources=[PERSISTED_JOURNAL_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_journal_entry(
    request: DecisionJournalCreateRequest,
    db: Session | None = None,
    user: User | None = None,
) -> DecisionJournalEntryResponse:
    if db is None or user is None:
        return _preview_entry(request)

    entry = DecisionJournalEntry(
        id=str(uuid4()),
        user_id=user.id,
        decision_type=request.decision_type,
        title=request.title.strip(),
        asset_symbol=request.asset_symbol.strip().upper() if request.asset_symbol else None,
        reason=request.reason.strip(),
        expected_outcome=request.expected_outcome.strip(),
        risk_considered=request.risk_considered.strip(),
        review_date=_parse_date(request.review_date),
        status="open",
    )
    db.add(entry)
    db.flush()
    return _build_entry_response(entry)


def update_journal_entry(
    db: Session,
    user: User,
    entry_id: str,
    request: DecisionJournalUpdateRequest,
) -> DecisionJournalEntryResponse:
    entry = _get_user_entry_or_404(db, user, entry_id)
    if request.title is not None:
        entry.title = request.title.strip()
    if request.reason is not None:
        entry.reason = request.reason.strip()
    if request.expected_outcome is not None:
        entry.expected_outcome = request.expected_outcome.strip()
    if request.risk_considered is not None:
        entry.risk_considered = request.risk_considered.strip()
    if request.review_date is not None:
        entry.review_date = _parse_date(request.review_date)
    if request.status is not None:
        entry.status = request.status
    if request.actual_outcome is not None:
        entry.actual_outcome = request.actual_outcome.strip() or None
    if request.reflection is not None:
        entry.reflection = request.reflection.strip() or None

    db.add(entry)
    db.flush()
    return _build_entry_response(entry)


def delete_journal_entry(db: Session, user: User, entry_id: str) -> DeleteRecordResponse:
    entry = _get_user_entry_or_404(db, user, entry_id)
    db.delete(entry)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=entry_id)


def _sample_journal() -> DecisionJournalResponse:
    entries = [
        DecisionJournalEntryResponse(
            id="journal_rebalance_review",
            decision_type="rebalance",
            title="Review tech allocation after market move",
            asset_symbol="STOCKS",
            reason="Tech-heavy holdings felt more volatile than expected during a sample market week.",
            expected_outcome="Understand whether the portfolio is still aligned with the time horizon.",
            risk_considered="Selling too quickly could create taxes or drift away from the long-term plan.",
            review_date="2026-06-15",
            created_at="2026-05-06T10:30:00-04:00",
            status="open",
            feedback_summary="Good decision framing: it separates review from an immediate trade.",
        ),
        DecisionJournalEntryResponse(
            id="journal_debt_paydown",
            decision_type="debt_payoff",
            title="Compare credit card payoff with extra investing",
            asset_symbol=None,
            reason="The sample credit card rate is much higher than other debts.",
            expected_outcome="Reduce interest pressure and improve monthly flexibility.",
            risk_considered="Using too much cash could weaken the emergency fund.",
            review_date="2026-07-01",
            created_at="2026-05-06T11:00:00-04:00",
            status="open",
            feedback_summary="Strong entry: it names the tradeoff between interest savings and liquidity.",
        ),
    ]

    return DecisionJournalResponse(
        entries=entries,
        feedback_prompts=[
            "Did the decision match the reason recorded at the time?",
            "Was the risk considered specific enough?",
            "What would you change about the decision process next time?",
        ],
        beginner_summary=(
            "A decision journal helps you learn from your reasoning instead of judging every choice only by short-term results."
        ),
        confidence="medium",
        data_limitations=[
            "Uses sample journal entries only.",
            "Sign in to save your own entries.",
            "Feedback is rule-based and educational.",
        ],
        sources=[JOURNAL_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _preview_entry(request: DecisionJournalCreateRequest) -> DecisionJournalEntryResponse:
    symbol = request.asset_symbol.upper() if request.asset_symbol else None
    return DecisionJournalEntryResponse(
        id=f"journal_preview_{int(datetime.now(tz=UTC).timestamp())}",
        decision_type=request.decision_type,
        title=request.title,
        asset_symbol=symbol,
        reason=request.reason,
        expected_outcome=request.expected_outcome,
        risk_considered=request.risk_considered,
        review_date=request.review_date,
        created_at=datetime.now(tz=UTC).isoformat(),
        status="open",
        feedback_summary=_feedback_for(request.reason, request.risk_considered),
    )


def _build_entry_response(entry: DecisionJournalEntry) -> DecisionJournalEntryResponse:
    return DecisionJournalEntryResponse(
        id=entry.id,
        decision_type=entry.decision_type,
        title=entry.title,
        asset_symbol=entry.asset_symbol,
        reason=entry.reason,
        expected_outcome=entry.expected_outcome or "",
        risk_considered=entry.risk_considered or "",
        review_date=entry.review_date.isoformat() if entry.review_date else "",
        created_at=entry.created_at.isoformat(),
        status=entry.status if entry.status in {"open", "reviewed"} else "open",
        feedback_summary=_feedback_for(entry.reason, entry.risk_considered or ""),
        actual_outcome=entry.actual_outcome,
        reflection=entry.reflection,
    )


def _get_user_entry_or_404(db: Session, user: User, entry_id: str) -> DecisionJournalEntry:
    entry = db.scalar(
        select(DecisionJournalEntry)
        .where(DecisionJournalEntry.id == entry_id)
        .where(DecisionJournalEntry.user_id == user.id)
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry was not found.")
    return entry


def _feedback_for(reason: str, risk_considered: str) -> str:
    risk_words = len(risk_considered.split())
    reason_words = len(reason.split())

    if risk_words >= 8 and reason_words >= 8:
        return "Strong entry: you wrote both a clear reason and a specific risk to review later."
    if risk_words < 8:
        return "Consider making the risk more specific so future-you can judge the decision process more fairly."
    return "Good start: consider adding more detail about why this decision matches your goal or time horizon."


def _parse_date(value: str | None) -> date | None:
    if value is None or not value.strip():
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Date must use YYYY-MM-DD.") from exc
