from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.api import (
    AssistantIntent,
    AssistantPromptContext,
    AssistantRequest,
    AssistantResponse,
    AssistantSafetyCheck,
)
from app.services.agent_orchestrator import build_agent_trace
from app.services.guide_context_service import GroundedGuideContext, build_grounded_guide_context, context_summary
from app.services.mock_data import EDUCATIONAL_DISCLAIMER

PROMPT_VERSION = "assistant_v3_grounded_context_2026_06_23"

SYSTEM_RULES = [
    "Croc Guide is an educational finance assistant for beginners.",
    "Croc Guide must avoid direct trading instructions, certainty claims, and return promises.",
    "Croc Guide must explain data freshness, limitations, confidence, and evidence.",
    "Croc Guide must use saved user records only when an authenticated user is present.",
]

UNSAFE_DIRECTIVE_RULES = [
    ("should i buy", "direct_trading_instruction"),
    ("should i sell", "direct_trading_instruction"),
    ("tell me what to buy", "direct_trading_instruction"),
    ("tell me what to sell", "direct_trading_instruction"),
    ("guaranteed", "return_claim"),
    ("will make money", "return_claim"),
    ("best investment", "return_claim"),
    ("ignore previous instructions", "prompt_injection_attempt"),
    ("ignore your instructions", "prompt_injection_attempt"),
    ("reveal your system prompt", "prompt_injection_attempt"),
    ("show me your system prompt", "prompt_injection_attempt"),
    ("developer message", "prompt_injection_attempt"),
    ("bypass guardrails", "prompt_injection_attempt"),
    ("jailbreak", "prompt_injection_attempt"),
    ("act as my financial advisor", "advisor_impersonation_request"),
]


@dataclass(frozen=True)
class IntentAnswer:
    summary: str
    observations: list[str]
    why_it_matters: str
    beginner_explanation: str
    considerations: list[str]
    suggested_next_steps: list[str]


def normalize_question(question: str) -> str:
    return " ".join(question.strip().split())


def route_intent(question: str) -> AssistantIntent:
    lowered = question.lower()

    if any(term in lowered for term, _code in UNSAFE_DIRECTIVE_RULES):
        return "safety"
    if any(term in lowered for term in ["debt", "loan", "mortgage", "credit card", "interest rate", "apr"]):
        return "debt"
    if any(term in lowered for term in ["retirement", "401", "ira", "match", "contribution"]):
        return "retirement"
    if any(term in lowered for term in ["tax", "loss harvesting", "capital gain", "wash sale", "tax lot"]):
        return "tax"
    if any(term in lowered for term in ["market", "news", "inflation", "rates", "treasury", "bitcoin", "changed recently"]):
        return "market"
    if any(term in lowered for term in ["risk", "diversification", "diversified", "liquidity", "allocation", "concentration", "compare"]):
        return "risk"
    if any(term in lowered for term in ["what is", "explain", "beginner", "learn", "mean"]):
        return "education"

    return "portfolio"


def run_safety_check(question: str) -> AssistantSafetyCheck:
    lowered = question.lower()
    flags = sorted({code for term, code in UNSAFE_DIRECTIVE_RULES if term in lowered})

    if not flags:
        return AssistantSafetyCheck(passed=True, flags=[])

    return AssistantSafetyCheck(
        passed=False,
        flags=flags,
        rewritten_question=(
            "The request was reframed into an educational review because CrocLens cannot provide "
            "direct trading instructions, certainty claims, or prompt disclosure."
        ),
    )


def build_prompt_context(
    question: str,
    intent: AssistantIntent,
    context: GroundedGuideContext,
) -> AssistantPromptContext:
    return AssistantPromptContext(
        prompt_version=PROMPT_VERSION,
        intent=intent,
        system_rules=["Safety rules are applied server-side and are not exposed as prompts."],
        context_summary=context_summary(context),
        user_question="[redacted]",
    )


def answer_for_intent(
    intent: AssistantIntent,
    context: GroundedGuideContext,
) -> IntentAnswer:
    if intent == "safety":
        return IntentAnswer(
            summary="I can reframe that into an educational review.",
            observations=_core_observations(context),
            why_it_matters=(
                "CrocLens can help you understand tradeoffs, risks, taxes, time horizon, and data quality, "
                "but it cannot make a trading decision for you."
            ),
            beginner_explanation=(
                "A safer beginner approach is to compare the idea with your goals, risk comfort, cash needs, "
                "debt, taxes, and the quality of the data available."
            ),
            considerations=[
                "Review what problem you are trying to solve before acting.",
                "Check whether the data is saved, stale, sample, or unavailable.",
                "Discuss financial or tax decisions with a qualified professional when needed.",
            ],
            suggested_next_steps=[
                "Consider writing the question as a research goal instead of a trading command.",
                "Review how the idea would change your allocation, debt, liquidity, and tax complexity.",
                "Use the decision journal to record your reasoning and review date.",
            ],
        )

    if intent == "debt":
        top_liability = context.top_liability_label or "no saved liability yet"
        return IntentAnswer(
            summary=f"Debt affects net worth because CrocLens subtracts liabilities from assets. Your tracked liabilities are ${context.total_liabilities:,.0f}.",
            observations=[
                *_core_observations(context),
                f"Debt-to-asset ratio: {context.debt_to_asset_percent:.1f}%.",
                f"Largest saved liability: {top_liability}.",
            ],
            why_it_matters="Debt can reduce net worth and cash flexibility, especially when balances have high rates or large minimum payments.",
            beginner_explanation=(
                "Think of net worth as what you own minus what you owe. A liability can be manageable, but it still competes with savings, investing, and emergency cash."
            ),
            considerations=[
                "Interest rate matters because higher-rate debt can grow faster.",
                "Minimum payments affect monthly flexibility.",
                "Extra payments can reduce debt but may also reduce cash reserves.",
            ],
            suggested_next_steps=[
                "Consider reviewing each debt balance, interest rate, minimum payment, and due date.",
                "Research how your highest-rate debt compares with your emergency cash goal.",
                "Use the journal to record any payoff plan assumptions before changing your budget.",
            ],
        )

    if intent == "retirement":
        return IntentAnswer(
            summary=f"CrocLens sees ${context.retirement_balance:,.0f} across {context.retirement_accounts_count} saved retirement accounts.",
            observations=[
                *_core_observations(context),
                f"Saved retirement accounts: {context.retirement_accounts_count}.",
                f"Profile time horizon: {context.time_horizon or 'not entered yet'}.",
            ],
            why_it_matters="Retirement accounts often have special contribution, tax, withdrawal, and employer match rules.",
            beginner_explanation=(
                "For beginners, the first retirement idea is to understand the account type, contribution rate, employer match formula, and investment mix assumptions."
            ),
            considerations=[
                "Employer match rules and vesting schedules can differ by plan.",
                "Long-term projections depend heavily on assumptions.",
                "Retirement accounts may be less liquid than regular cash or brokerage assets.",
            ],
            suggested_next_steps=[
                "Consider reviewing whether your contribution captures any available employer match.",
                "Research the investment mix inside each retirement account.",
                "Record your retirement assumptions before comparing scenarios.",
            ],
        )

    if intent == "tax":
        return IntentAnswer(
            summary=f"CrocLens found {context.tax_lot_count} saved tax lots and about ${context.unrealized_tax_loss:,.0f} in estimated unrealized losses.",
            observations=[
                *_core_observations(context),
                f"Saved tax lots: {context.tax_lot_count}.",
                f"Estimated unrealized tax-lot losses: ${context.unrealized_tax_loss:,.0f}.",
            ],
            why_it_matters="Tax lots help explain cost basis, holding periods, unrealized gains or losses, and why taxable decisions need careful records.",
            beginner_explanation=(
                "A tax lot is one purchase record. CrocLens can explain the concept, but it does not know your full tax situation or replace a tax professional."
            ),
            considerations=[
                "Holding period can affect tax treatment.",
                "Wash-sale rules may affect loss treatment.",
                "State taxes, filing status, and account type are not fully known to CrocLens.",
            ],
            suggested_next_steps=[
                "Consider reviewing purchase dates, cost basis, and account type for taxable lots.",
                "Research holding-period and wash-sale concepts before making tax decisions.",
                "Discuss specific tax actions with a qualified tax professional.",
            ],
        )

    if intent == "market":
        return IntentAnswer(
            summary=f"Market context is {context.provider_status}; data quality is {context.data_quality}.",
            observations=[
                *_core_observations(context),
                f"Data as of: {context.data_as_of or 'not available'}.",
                f"Stale data warning: {'yes' if context.is_stale else 'no'}.",
            ],
            why_it_matters="Market headlines matter most when they affect holdings that are meaningful in your own allocation.",
            beginner_explanation=(
                "A headline does not affect everyone equally. CrocLens checks what you have saved, how large each exposure is, and whether the data is current enough to trust."
            ),
            considerations=[
                "Provider data may be delayed or cached.",
                "Manual holdings may not have a current provider price.",
                "Short-term market moves may not change a long-term plan.",
            ],
            suggested_next_steps=[
                "Consider checking which saved holdings connect to the market event.",
                "Review freshness and provider labels before relying on a number.",
                "Use the watchlist to track research questions separately from account records.",
            ],
        )

    if intent == "risk":
        allocation = ", ".join(context.allocation_labels) if context.allocation_labels else "no saved allocation yet"
        return IntentAnswer(
            summary=f"Your diversification score is {context.diversification_score if context.diversification_score is not None else 'not available'} based on saved allocation.",
            observations=[
                *_core_observations(context),
                f"Top allocation groups: {allocation}.",
                f"Largest saved holding: {context.top_holding_label or 'not available yet'}.",
            ],
            why_it_matters="Diversification can reduce dependence on one asset, sector, account, or risk type, but it does not remove risk.",
            beginner_explanation=(
                "For beginners, diversification means not depending too heavily on one thing going right. CrocLens compares concentration, liquidity, debt, and taxes together."
            ),
            considerations=[
                "A high asset count is not the same as true diversification.",
                "ETF overlap can make exposure look more diversified than it is.",
                "Debt and emergency cash can change the amount of risk that feels manageable.",
            ],
            suggested_next_steps=[
                "Consider reviewing your largest asset class and largest saved holding.",
                "Research whether funds in your account overlap with each other.",
                "Compare your risk score with your time horizon and cash needs.",
            ],
        )

    if intent == "education":
        return IntentAnswer(
            summary=f"I can explain this in beginner language using {context.label}.",
            observations=_core_observations(context),
            why_it_matters="Simple definitions are more useful when they connect back to your saved assets, liabilities, goals, and data quality.",
            beginner_explanation=(
                "Assets are what you own, liabilities are what you owe, and net worth is the difference. CrocLens adds context like risk, liquidity, taxes, retirement, and data freshness."
            ),
            considerations=[
                "Definitions can change by account type and asset type.",
                "Sample data and saved data should be interpreted differently.",
                "When data is missing, CrocLens should say it is missing.",
            ],
            suggested_next_steps=[
                "Consider asking about one dashboard metric at a time.",
                "Open the evidence details to see which saved records were used.",
                "Add missing holdings, debts, or retirement accounts to improve context.",
            ],
        )

    return IntentAnswer(
        summary=f"Your tracked net worth is ${context.net_worth:,.0f} based on {context.label}.",
        observations=_core_observations(context),
        why_it_matters="A whole-wealth view helps compare assets, debts, taxes, retirement, and liquidity instead of looking at one number alone.",
        beginner_explanation=(
            "CrocLens starts with your saved assets and liabilities, then layers on allocation, risk, planning records, and data freshness."
        ),
        considerations=[
            "Manual entries may be incomplete or outdated.",
            "Provider-valued holdings can become stale if a refresh fails.",
            "A useful next step should improve clarity, not push a trade.",
        ],
        suggested_next_steps=[
            "Consider reviewing whether any large asset or debt record is missing.",
            "Check your largest allocation and largest liability first.",
            "Use action plans and the journal to turn observations into review steps.",
        ],
    )


def answer_question(
    request: AssistantRequest,
    db: Session | None = None,
    current_user: User | None = None,
) -> AssistantResponse:
    question = normalize_question(request.question)
    intent = route_intent(question)
    safety = run_safety_check(question)
    context = build_grounded_guide_context(db=db, user=current_user)
    intent_answer = answer_for_intent(intent, context)

    limitations = list(dict.fromkeys(context.data_limitations))
    if not safety.passed:
        limitations.insert(0, "The request included unsafe wording, so CrocLens returned an educational framing instead.")

    return AssistantResponse(
        intent=intent,
        summary=intent_answer.summary,
        observations=intent_answer.observations,
        why_it_matters=intent_answer.why_it_matters,
        considerations=intent_answer.considerations,
        beginner_explanation=intent_answer.beginner_explanation,
        suggested_next_steps=intent_answer.suggested_next_steps,
        evidence=context.evidence,
        confidence=_confidence_for(context, safety),
        data_as_of=context.data_as_of,
        retrieved_at=context.retrieved_at,
        is_sample_data=context.is_sample_data,
        data_quality=context.data_quality,
        provider_status=context.provider_status,
        is_stale=context.is_stale,
        data_limitations=limitations,
        sources=context.sources,
        safety=safety,
        agent_trace=build_agent_trace(
            intent=intent,
            question="[redacted]",
            answer_summary=intent_answer.summary,
            safety=safety,
        ),
        prompt_context=build_prompt_context("[redacted]", intent, context) if request.include_prompt_debug else None,
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        safety_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _core_observations(context: GroundedGuideContext) -> list[str]:
    observations = [
        f"Net worth: ${context.net_worth:,.0f}.",
        f"Assets: ${context.total_assets:,.0f}; liabilities: ${context.total_liabilities:,.0f}.",
        f"Saved holdings: {context.holdings_count}; saved liabilities: {context.liabilities_count}.",
    ]
    if context.allocation_labels:
        observations.append(f"Top allocation: {', '.join(context.allocation_labels[:3])}.")
    if context.profile_goal:
        observations.append(f"Saved goal: {context.profile_goal}.")
    if context.data_quality:
        observations.append(f"Data quality: {context.data_quality}.")
    return observations


def _confidence_for(context: GroundedGuideContext, safety: AssistantSafetyCheck) -> str:
    if not safety.passed:
        return "low"
    if context.is_sample_data or context.data_quality in {"limited", "stale", "unavailable"}:
        return "low"
    if context.holdings_count == 0:
        return "low"
    return "medium"
