from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RetirementAccount, User
from app.schemas.api import (
    DeleteRecordResponse,
    EmployerMatchResponse,
    RetirementAccountCreateRequest,
    RetirementAccountResponse,
    RetirementAccountUpdateRequest,
    RetirementPlanResponse,
    RetirementScenarioResponse,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


RETIREMENT_SOURCE = SourceMetadata(
    name="CrocLens sample retirement profile",
    freshness="Sample retirement planning assumptions",
    as_of="2026-05-06",
)

PERSISTED_RETIREMENT_SOURCE = SourceMetadata(
    name="CrocLens retirement records",
    freshness="Saved user retirement accounts",
    as_of=date.today().isoformat(),
)

SAMPLE_SALARY = 82_000
CURRENT_AGE = 32
RETIREMENT_AGE = 65
TARGET_BALANCE = 1_200_000


def get_retirement_plan(db: Session | None = None, user: User | None = None) -> RetirementPlanResponse:
    if db is None or user is None:
        return _sample_retirement_plan()

    accounts = list(
        db.scalars(
            select(RetirementAccount)
            .where(RetirementAccount.user_id == user.id)
            .order_by(RetirementAccount.created_at.asc())
        )
    )
    responses = [_build_account_response(account) for account in accounts]
    current_balance = round(sum(account.current_balance for account in responses), 2)
    contribution_percent = _primary_contribution_percent(accounts)
    employer_match = _employer_match_for(contribution_percent, accounts)

    return RetirementPlanResponse(
        headline=(
            "Your saved retirement accounts are ready for review."
            if accounts
            else "Add a retirement account to start tracking progress."
        ),
        progress_percent=min(100, round((current_balance / TARGET_BALANCE) * 100)),
        target_retirement_balance=TARGET_BALANCE,
        current_retirement_balance=current_balance,
        accounts=responses,
        employer_match=employer_match,
        scenarios=[
            _scenario("current", "Current saved contribution", current_balance, contribution_percent, accounts),
            _scenario("plus_two", "Increase by 2 percentage points", current_balance, min(100, contribution_percent + 2), accounts),
            _scenario("stretch", "Stretch review scenario", current_balance, min(100, max(contribution_percent, 10)), accounts),
        ],
        beginner_summary=(
            "Retirement planning is a long-term estimate. CrocLens uses your saved balances and contribution rates to explain scenarios, not to guarantee outcomes."
        ),
        suggested_reviews=[
            "Consider reviewing whether each account balance is current.",
            "You may want to research whether your contribution captures any available employer match.",
            "Review fees, investment mix, taxes, and time horizon before changing contributions.",
        ],
        confidence="medium",
        data_limitations=[
            "Uses saved CrocLens retirement account records.",
            "Salary, age, future returns, taxes, fees, and inflation are simplified educational assumptions.",
            "Projected balances are educational estimates, not guaranteed outcomes.",
        ],
        sources=[PERSISTED_RETIREMENT_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_retirement_account(db: Session, user: User, request: RetirementAccountCreateRequest) -> RetirementAccountResponse:
    account = RetirementAccount(
        id=str(uuid4()),
        user_id=user.id,
        account_type=request.account_type.strip(),
        provider_name=_clean_optional(request.provider_name),
        balance=_to_decimal(request.current_balance),
        contribution_percent=_optional_decimal(request.contribution_percent),
        employer_match_percent=_optional_decimal(request.employer_match_percent),
    )
    db.add(account)
    db.flush()
    return _build_account_response(account)


def update_retirement_account(
    db: Session,
    user: User,
    account_id: str,
    request: RetirementAccountUpdateRequest,
) -> RetirementAccountResponse:
    account = _get_user_retirement_account_or_404(db, user, account_id)
    if request.account_type is not None:
        account.account_type = request.account_type.strip()
    if request.provider_name is not None:
        account.provider_name = _clean_optional(request.provider_name)
    if request.current_balance is not None:
        account.balance = _to_decimal(request.current_balance)
    if request.contribution_percent is not None:
        account.contribution_percent = _to_decimal(request.contribution_percent)
    if request.employer_match_percent is not None:
        account.employer_match_percent = _to_decimal(request.employer_match_percent)

    db.add(account)
    db.flush()
    return _build_account_response(account)


def delete_retirement_account(db: Session, user: User, account_id: str) -> DeleteRecordResponse:
    account = _get_user_retirement_account_or_404(db, user, account_id)
    db.delete(account)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=account_id)


def _sample_retirement_plan() -> RetirementPlanResponse:
    accounts = [
        RetirementAccountResponse(
            id="ret_401k",
            account_type="401(k)",
            provider_name="Sample employer plan",
            current_balance=38_400,
            contribution_percent=4,
            annual_contribution_estimate=round(SAMPLE_SALARY * 0.04, 2),
            investment_mix_summary="Mostly diversified stock and bond funds in sample data.",
        ),
        RetirementAccountResponse(
            id="ret_roth_ira",
            account_type="Roth IRA",
            provider_name="Sample IRA provider",
            current_balance=4_422,
            contribution_percent=0,
            annual_contribution_estimate=0,
            investment_mix_summary="Long-term retirement bucket; contribution assumptions are not connected yet.",
        ),
    ]
    current_balance = round(sum(account.current_balance for account in accounts), 2)

    return RetirementPlanResponse(
        headline="You are building retirement momentum, and the employer match is worth understanding.",
        progress_percent=round((current_balance / TARGET_BALANCE) * 100),
        target_retirement_balance=TARGET_BALANCE,
        current_retirement_balance=current_balance,
        accounts=accounts,
        employer_match=_sample_employer_match_for(4),
        scenarios=[
            _sample_scenario("current", "Current 4% contribution", 4),
            _sample_scenario("match", "Increase to full sample match", 6),
            _sample_scenario("stretch", "Stretch scenario", 10),
        ],
        beginner_summary=(
            "Retirement planning is a long-term estimate. CrocLens shows how contribution rate and employer match "
            "can change the path, but the numbers are not guarantees."
        ),
        suggested_reviews=[
            "Consider reviewing whether you understand the employer match formula.",
            "You may want to research whether your current contribution captures the full sample match.",
            "Review investment mix, fees, and time horizon before changing contributions.",
        ],
        confidence="medium",
        data_limitations=[
            "Uses sample salary, age, account balances, and return assumptions.",
            "Does not know actual employer plan rules, tax bracket, spending needs, or inflation assumptions.",
            "Projected balances are educational estimates, not guaranteed outcomes.",
        ],
        sources=[RETIREMENT_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _build_account_response(account: RetirementAccount) -> RetirementAccountResponse:
    contribution_percent = _to_float(account.contribution_percent)
    return RetirementAccountResponse(
        id=account.id,
        account_type=account.account_type,
        provider_name=account.provider_name or "Retirement account",
        current_balance=_to_float(account.balance),
        contribution_percent=contribution_percent,
        annual_contribution_estimate=round(SAMPLE_SALARY * contribution_percent / 100, 2),
        investment_mix_summary="Saved retirement account. Add investment mix details in a later planning slice.",
    )


def _employer_match_for(contribution_percent: float, accounts: list[RetirementAccount]) -> EmployerMatchResponse:
    match_percent = max((_to_float(account.employer_match_percent) for account in accounts), default=0)
    estimated_match = round(SAMPLE_SALARY * min(contribution_percent, match_percent) / 100, 2) if match_percent else 0
    return EmployerMatchResponse(
        has_match=match_percent > 0,
        formula=(
            f"Saved match estimate: up to {match_percent:.1f}% of salary."
            if match_percent
            else "No employer match percentage saved yet."
        ),
        estimated_annual_match=estimated_match,
        beginner_explanation=(
            "Employer match is extra retirement money from an employer when the employee contributes, subject to plan rules."
        ),
    )


def _scenario(
    scenario_id: str,
    label: str,
    current_balance: float,
    contribution_percent: float,
    accounts: list[RetirementAccount],
) -> RetirementScenarioResponse:
    employee_contribution = round(SAMPLE_SALARY * contribution_percent / 100, 2)
    employer_match = _employer_match_for(contribution_percent, accounts).estimated_annual_match
    years = RETIREMENT_AGE - CURRENT_AGE
    simple_growth_factor = 1 + (years * 0.045)
    projected_balance = round((current_balance + (employee_contribution + employer_match) * years) * simple_growth_factor, 2)

    return RetirementScenarioResponse(
        id=scenario_id,
        label=label,
        contribution_percent=contribution_percent,
        estimated_annual_employee_contribution=employee_contribution,
        estimated_annual_employer_match=employer_match,
        projected_balance_at_65=max(0, projected_balance),
        assumptions=[
            f"Educational salary assumption: ${SAMPLE_SALARY:,}.",
            "Simple projection using a 4.5% annualized growth assumption.",
            "No taxes, fees, inflation, income changes, or sequence risk modeled.",
        ],
    )


def _sample_employer_match_for(contribution_percent: float) -> EmployerMatchResponse:
    matched_percent = min(contribution_percent, 6)
    estimated_match = round(SAMPLE_SALARY * matched_percent * 0.5 / 100, 2)
    return EmployerMatchResponse(
        has_match=True,
        formula="Sample match: 50% of employee contributions up to 6% of salary.",
        estimated_annual_match=estimated_match,
        beginner_explanation=(
            "An employer match is extra retirement money from the employer when the employee contributes. "
            "It is usually limited by plan rules."
        ),
    )


def _sample_scenario(scenario_id: str, label: str, contribution_percent: float) -> RetirementScenarioResponse:
    employee_contribution = round(SAMPLE_SALARY * contribution_percent / 100, 2)
    employer_match = _sample_employer_match_for(contribution_percent).estimated_annual_match
    years = RETIREMENT_AGE - CURRENT_AGE
    simple_growth_factor = 1 + (years * 0.045)
    projected_balance = round((42_822 + (employee_contribution + employer_match) * years) * simple_growth_factor, 2)
    return RetirementScenarioResponse(
        id=scenario_id,
        label=label,
        contribution_percent=contribution_percent,
        estimated_annual_employee_contribution=employee_contribution,
        estimated_annual_employer_match=employer_match,
        projected_balance_at_65=projected_balance,
        assumptions=[
            f"Sample salary: ${SAMPLE_SALARY:,}.",
            "Simple educational projection using a 4.5% annualized growth assumption.",
            "No taxes, fees, inflation, income changes, or market sequence risk modeled yet.",
        ],
    )


def _get_user_retirement_account_or_404(db: Session, user: User, account_id: str) -> RetirementAccount:
    account = db.scalar(
        select(RetirementAccount)
        .where(RetirementAccount.id == account_id)
        .where(RetirementAccount.user_id == user.id)
    )
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Retirement account was not found.")
    return account


def _primary_contribution_percent(accounts: list[RetirementAccount]) -> float:
    return max((_to_float(account.contribution_percent) for account in accounts), default=0)


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _to_decimal(value: float | int | Decimal) -> Decimal:
    return Decimal(str(value))


def _optional_decimal(value: float | int | Decimal | None) -> Decimal | None:
    return None if value is None else _to_decimal(value)


def _to_float(value: Decimal | float | int | None) -> float:
    return 0.0 if value is None else float(value)
