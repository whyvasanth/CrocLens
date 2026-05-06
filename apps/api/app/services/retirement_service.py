from app.schemas.api import (
    EmployerMatchResponse,
    RetirementAccountResponse,
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

SAMPLE_SALARY = 82_000
CURRENT_AGE = 32
RETIREMENT_AGE = 65
TARGET_BALANCE = 1_200_000


def get_retirement_plan() -> RetirementPlanResponse:
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

    employer_match = _employer_match_for(4)
    scenarios = [
        _scenario("current", "Current 4% contribution", 4),
        _scenario("match", "Increase to full sample match", 6),
        _scenario("stretch", "Stretch scenario", 10),
    ]

    return RetirementPlanResponse(
        headline="You are building retirement momentum, and the employer match is worth understanding.",
        progress_percent=round((current_balance / TARGET_BALANCE) * 100),
        target_retirement_balance=TARGET_BALANCE,
        current_retirement_balance=current_balance,
        accounts=accounts,
        employer_match=employer_match,
        scenarios=scenarios,
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


def _employer_match_for(contribution_percent: float) -> EmployerMatchResponse:
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


def _scenario(scenario_id: str, label: str, contribution_percent: float) -> RetirementScenarioResponse:
    employee_contribution = round(SAMPLE_SALARY * contribution_percent / 100, 2)
    employer_match = _employer_match_for(contribution_percent).estimated_annual_match
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
