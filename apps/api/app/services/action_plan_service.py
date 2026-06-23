from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActionPlan, User
from app.schemas.api import ActionPlanItem, ActionPlanResponse, ActionPlanStatusResponse
from app.services.mock_data import EDUCATIONAL_DISCLAIMER, generate_action_plan as generate_sample_action_plan
from app.services.portfolio_service import get_user_portfolio_summary, list_user_liabilities


def get_action_plan_for_user(db: Session | None = None, user: User | None = None) -> ActionPlanResponse:
    if db is None or user is None:
        return generate_sample_action_plan()

    plans = _active_user_plans(db, user)
    if not plans:
        _seed_user_action_plans(db, user)
        plans = _active_user_plans(db, user)

    return _build_response(user, plans)


def generate_action_plan_for_user(db: Session | None = None, user: User | None = None) -> ActionPlanResponse:
    if db is None or user is None:
        return generate_sample_action_plan()

    if not _active_user_plans(db, user):
        _seed_user_action_plans(db, user)
    return _build_response(user, _active_user_plans(db, user))


def complete_action_plan_item(db: Session, user: User, item_id: str) -> ActionPlanStatusResponse:
    item = _get_user_action_item_or_404(db, user, item_id)
    item.status = "completed"
    item.completed_at = datetime.now(tz=UTC)
    item.dismissed_at = None
    db.add(item)
    db.flush()
    return ActionPlanStatusResponse(
        item=_build_item(item),
        action="completed",
        explanation="Marked complete. CrocLens records this as a review step you finished, not as proof that a financial outcome is guaranteed.",
    )


def dismiss_action_plan_item(db: Session, user: User, item_id: str) -> ActionPlanStatusResponse:
    item = _get_user_action_item_or_404(db, user, item_id)
    item.status = "dismissed"
    item.dismissed_at = datetime.now(tz=UTC)
    db.add(item)
    db.flush()
    return ActionPlanStatusResponse(
        item=_build_item(item, override_status="suggested"),
        action="dismissed",
        explanation="Dismissed from the active list. You can reopen it later if the review becomes relevant again.",
    )


def reopen_action_plan_item(db: Session, user: User, item_id: str) -> ActionPlanStatusResponse:
    item = _get_user_action_item_or_404(db, user, item_id)
    item.status = "suggested"
    item.completed_at = None
    item.dismissed_at = None
    db.add(item)
    db.flush()
    return ActionPlanStatusResponse(
        item=_build_item(item),
        action="reopened",
        explanation="Reopened as a suggested review item.",
    )


def _active_user_plans(db: Session, user: User) -> list[ActionPlan]:
    return list(
        db.scalars(
            select(ActionPlan)
            .where(ActionPlan.user_id == user.id)
            .where(ActionPlan.dismissed_at.is_(None))
            .order_by(ActionPlan.created_at.asc())
        )
    )


def _seed_user_action_plans(db: Session, user: User) -> None:
    summary = get_user_portfolio_summary(db, user)
    liabilities = list_user_liabilities(db, user)
    generated: list[ActionPlan] = []

    if summary.total_assets == 0:
        generated.append(
            _new_plan(
                user=user,
                title="Add your first tracked asset",
                description="Consider adding cash, an ETF, a retirement account, or another asset so CrocLens can calculate a personal net worth baseline.",
                priority="high",
                evidence=["No saved assets are currently tracked."],
            )
        )
    else:
        generated.append(
            _new_plan(
                user=user,
                title="Review your largest allocation",
                description="Consider reviewing whether your largest asset group still matches your goal, time horizon, and comfort with risk.",
                priority="medium",
                evidence=[f"Saved net worth: ${summary.net_worth:,.2f}.", f"Tracked assets: ${summary.total_assets:,.2f}."],
            )
        )

    high_interest = [liability for liability in liabilities if liability.interest_rate is not None and liability.interest_rate >= 10]
    if high_interest:
        generated.append(
            _new_plan(
                user=user,
                title="Compare high-interest debt pressure",
                description="You may want to research how high-interest debt affects monthly flexibility and net worth growth.",
                priority="high",
                evidence=[f"{len(high_interest)} saved liability record(s) have rates at or above 10%."],
            )
        )

    generated.append(
        _new_plan(
            user=user,
            title="Check data freshness labels",
            description="Review which dashboard values are user-entered, provider-valued, stale, or unavailable before relying on them.",
            priority="low",
            evidence=["CrocLens separates manual values from provider-valued data."],
        )
    )

    for plan in generated:
        db.add(plan)
    db.flush()


def _new_plan(user: User, title: str, description: str, priority: str, evidence: list[str]) -> ActionPlan:
    return ActionPlan(
        id=str(uuid4()),
        user_id=user.id,
        title=title,
        status="suggested",
        priority=priority,
        description=description,
        confidence="medium",
        data_limitations=[
            "Generated from saved CrocLens records.",
            "This is an educational review item, not financial advice.",
        ],
        evidence=evidence,
    )


def _get_user_action_item_or_404(db: Session, user: User, item_id: str) -> ActionPlan:
    item = db.scalar(select(ActionPlan).where(ActionPlan.id == item_id).where(ActionPlan.user_id == user.id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action plan item was not found.")
    return item


def _build_response(user: User, plans: list[ActionPlan]) -> ActionPlanResponse:
    return ActionPlanResponse(
        plan_id=f"user_plan_{user.id}",
        items=[_build_item(plan) for plan in plans if plan.status in {"suggested", "in_progress", "completed"}],
        confidence="medium",
        data_limitations=[
            "Generated from saved CrocLens records and transparent heuristics.",
            "Action items are educational review prompts, not instructions to buy, sell, or change accounts.",
        ],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _build_item(plan: ActionPlan, override_status: str | None = None) -> ActionPlanItem:
    status_value = override_status or plan.status
    if status_value not in {"suggested", "in_progress", "completed"}:
        status_value = "suggested"

    return ActionPlanItem(
        id=plan.id,
        title=plan.title,
        description=plan.description,
        priority=plan.priority if plan.priority in {"low", "medium", "high"} else "medium",
        status=status_value,
        safe_wording_note="Uses review and research language, not direct financial instructions.",
    )
