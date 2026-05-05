from app.schemas.api import (
    OnboardingOptionsResponse,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


ONBOARDING_SOURCE = SourceMetadata(
    name="CrocLens onboarding model",
    freshness="Calculated from the current onboarding form submission",
    as_of="2026-05-05",
)


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def get_onboarding_options() -> OnboardingOptionsResponse:
    return OnboardingOptionsResponse(
        investment_experience=["new", "some", "experienced"],
        primary_goal=["learn", "build_wealth", "retirement", "debt_payoff", "home", "emergency_fund"],
        risk_tolerance=["low", "medium", "high"],
        time_horizon=["short", "medium", "long"],
        income_range=["under_50k", "50k_100k", "100k_200k", "over_200k", "prefer_not"],
        employer_match=["yes", "no", "not_sure", "not_applicable"],
    )


def calculate_onboarding_risk_score(profile: OnboardingProfileRequest) -> int:
    tolerance_score = {
        "low": 30,
        "medium": 55,
        "high": 75,
    }[profile.risk_tolerance]

    experience_adjustment = {
        "new": -8,
        "some": 0,
        "experienced": 6,
    }[profile.investment_experience]

    horizon_adjustment = {
        "short": -10,
        "medium": 0,
        "long": 10,
    }[profile.time_horizon]

    goal_adjustment = {
        "learn": -4,
        "build_wealth": 6,
        "retirement": 4,
        "debt_payoff": -8,
        "home": -6,
        "emergency_fund": -10,
    }[profile.primary_goal]

    cash_adjustment = -10 if profile.emergency_cash_months < 3 else 5 if profile.emergency_cash_months >= 6 else 0
    debt_adjustment = -10 if profile.has_high_interest_debt else 0

    return clamp_score(
        tolerance_score
        + experience_adjustment
        + horizon_adjustment
        + goal_adjustment
        + cash_adjustment
        + debt_adjustment
    )


def classify_risk_profile(score: int) -> str:
    if score <= 40:
        return "Cautious Beginner"

    if score <= 70:
        return "Balanced Beginner"

    return "Growth-Oriented Beginner"


def build_personalization_notes(profile: OnboardingProfileRequest) -> list[str]:
    notes = []

    if profile.investment_experience == "new":
        notes.append("Beginner mode should stay on by default and explain every metric in plain language.")
    else:
        notes.append("CrocLens can show plain-language explanations while still using portfolio-level metrics.")

    if profile.emergency_cash_months < 3:
        notes.append("Cash-buffer explanations should appear early because emergency cash is below three months.")
    elif profile.emergency_cash_months >= 6:
        notes.append("Cash-buffer context can focus on opportunity cost because the sample buffer is stronger.")
    else:
        notes.append("Cash-buffer context should compare current cash with core monthly expenses.")

    if profile.has_high_interest_debt:
        notes.append("Action plans should flag high-interest debt as a possible drag on net worth growth.")

    if profile.has_retirement_account:
        if profile.employer_match == "not_sure":
            notes.append("Retirement guidance should explain employer match rules before advanced planning.")
        elif profile.employer_match == "yes":
            notes.append("Retirement guidance can highlight contribution and employer match awareness.")
    else:
        notes.append("Retirement onboarding should explain account types before contribution scenarios.")

    if profile.manual_assets:
        total_manual_assets = sum(asset.estimated_value for asset in profile.manual_assets)
        notes.append(f"Manual asset entry captured {len(profile.manual_assets)} item(s) worth about ${total_manual_assets:,.0f}.")
    else:
        notes.append("Manual asset entry is empty, so dashboard insights should clearly say sample data is still being used.")

    return notes


def build_recommended_first_steps(profile: OnboardingProfileRequest) -> list[str]:
    steps = []

    if profile.emergency_cash_months < 3:
        steps.append("Consider reviewing whether your emergency cash target covers at least a few months of core expenses.")

    if profile.has_high_interest_debt:
        steps.append("You may want to research how high-interest debt compares with investment risk and expected returns.")

    if profile.has_retirement_account and profile.employer_match == "not_sure":
        steps.append("Consider reviewing your employer match formula before changing retirement contributions.")
    elif not profile.has_retirement_account:
        steps.append("You may want to research basic retirement account types such as 401(k), traditional IRA, and Roth IRA.")

    if profile.primary_goal == "build_wealth":
        steps.append("Consider reviewing your asset allocation before adding more risk.")
    elif profile.primary_goal == "debt_payoff":
        steps.append("Consider comparing debt interest rates before choosing which balance to study first.")

    if len(steps) < 3:
        steps.append("Based on the data provided, review your top goal and time horizon before making major changes.")

    return steps[:4]


def create_onboarding_profile(profile: OnboardingProfileRequest) -> OnboardingProfileResponse:
    risk_score = calculate_onboarding_risk_score(profile)
    risk_profile = classify_risk_profile(risk_score)

    return OnboardingProfileResponse(
        profile_id="profile_mock_phase_8",
        risk_profile=risk_profile,
        risk_score=risk_score,
        summary=(
            f"CrocLens classifies this sample onboarding profile as {risk_profile}. "
            "This is a starting point for education, not a recommendation to take investment action."
        ),
        personalization_notes=build_personalization_notes(profile),
        recommended_first_steps=build_recommended_first_steps(profile),
        confidence="medium",
        data_limitations=[
            "Uses one form submission only.",
            "Does not include verified income, account balances, spending history, or live market data.",
            "Risk scoring is a simple educational heuristic for the MVP.",
        ],
        source=ONBOARDING_SOURCE,
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )
