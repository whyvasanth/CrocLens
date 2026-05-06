from datetime import UTC, datetime

from app.schemas.api import (
    DecisionJournalCreateRequest,
    DecisionJournalEntryResponse,
    DecisionJournalResponse,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


JOURNAL_SOURCE = SourceMetadata(
    name="CrocLens sample decision journal",
    freshness="Sample journal entries",
    as_of="2026-05-06",
)


def list_journal_entries() -> DecisionJournalResponse:
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
            "Entries are not persisted to a database yet.",
            "Feedback is rule-based and educational.",
        ],
        sources=[JOURNAL_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_journal_entry(request: DecisionJournalCreateRequest) -> DecisionJournalEntryResponse:
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
        feedback_summary=_feedback_for(request),
    )


def _feedback_for(request: DecisionJournalCreateRequest) -> str:
    risk_words = len(request.risk_considered.split())
    reason_words = len(request.reason.split())

    if risk_words >= 8 and reason_words >= 8:
        return "Strong entry: you wrote both a clear reason and a specific risk to review later."
    if risk_words < 8:
        return "Consider making the risk more specific so future-you can judge the decision process more fairly."
    return "Good start: consider adding more detail about why this decision matches your goal or time horizon."
