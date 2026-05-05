from dataclasses import dataclass

from app.schemas.api import (
    AssistantIntent,
    AssistantPromptContext,
    AssistantRequest,
    AssistantResponse,
    AssistantSafetyCheck,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER, MOCK_SOURCE, get_portfolio_summary

PROMPT_VERSION = "assistant_v1_rule_based_2026_05_05"

SYSTEM_RULES = [
    "You are Croc Guide, a friendly educational finance assistant for beginners.",
    "Do not provide direct buy, sell, or hold instructions.",
    "Do not promise returns or use guaranteed language.",
    "Use safe wording such as consider reviewing, you may want to research, and based on the data provided.",
    "Always include confidence, data limitations, source freshness, and an educational disclaimer.",
]

UNSAFE_DIRECTIVE_TERMS = [
    "should i buy",
    "should i sell",
    "tell me what to buy",
    "tell me what to sell",
    "guaranteed",
    "will make money",
    "best investment",
]


@dataclass(frozen=True)
class IntentAnswer:
    summary: str
    beginner_explanation: str
    suggested_next_steps: list[str]


def normalize_question(question: str) -> str:
    return " ".join(question.strip().split())


def route_intent(question: str) -> AssistantIntent:
    lowered = question.lower()

    if any(term in lowered for term in ["buy", "sell", "guaranteed", "best investment", "will make money"]):
        return "safety"
    if any(term in lowered for term in ["debt", "loan", "mortgage", "credit card", "interest rate", "apr"]):
        return "debt"
    if any(term in lowered for term in ["retirement", "401", "ira", "match", "contribution"]):
        return "retirement"
    if any(term in lowered for term in ["tax", "loss harvesting", "capital gain", "wash sale"]):
        return "tax"
    if any(term in lowered for term in ["market", "news", "inflation", "rates", "treasury", "bitcoin"]):
        return "market"
    if any(term in lowered for term in ["risk", "diversification", "liquidity", "allocation"]):
        return "risk"
    if any(term in lowered for term in ["what is", "explain", "beginner", "learn"]):
        return "education"

    return "portfolio"


def run_safety_check(question: str) -> AssistantSafetyCheck:
    lowered = question.lower()
    flags = [term for term in UNSAFE_DIRECTIVE_TERMS if term in lowered]

    if not flags:
        return AssistantSafetyCheck(passed=True, flags=[])

    return AssistantSafetyCheck(
        passed=False,
        flags=flags,
        rewritten_question=(
            "The question was reframed into an educational review because CrocLens cannot provide "
            "direct trading instructions or guaranteed-return claims."
        ),
    )


def build_prompt_context(question: str, intent: AssistantIntent) -> AssistantPromptContext:
    portfolio = get_portfolio_summary()
    context_summary = (
        f"Sample user {portfolio.user_name} has net worth ${portfolio.net_worth:,.0f}, "
        f"assets ${portfolio.total_assets:,.0f}, liabilities ${portfolio.total_liabilities:,.0f}, "
        f"and a debt-to-asset ratio of {portfolio.debt_impact.debt_to_asset_percent}%."
    )

    return AssistantPromptContext(
        prompt_version=PROMPT_VERSION,
        intent=intent,
        system_rules=SYSTEM_RULES,
        context_summary=context_summary,
        user_question=question,
    )


def answer_for_intent(intent: AssistantIntent, question: str, beginner_mode: bool) -> IntentAnswer:
    if intent == "safety":
        return IntentAnswer(
            summary="I can help you review the idea safely, but I cannot tell you to buy or sell anything.",
            beginner_explanation=(
                "A safer beginner approach is to compare the decision with your goals, risk comfort, "
                "time horizon, taxes, cash needs, and debt before taking action."
            ),
            suggested_next_steps=[
                "Consider reviewing why the investment interests you and what could go wrong.",
                "You may want to research how the asset fits with your overall allocation.",
                "This may be worth discussing with a licensed professional before making a trading decision.",
            ],
        )

    if intent == "debt":
        return IntentAnswer(
            summary="Debt can affect net worth because interest costs may slow progress toward other goals.",
            beginner_explanation=(
                "Based on the data provided, CrocLens compares debt with assets because wealth is what "
                "you own minus what you owe. Higher-interest debt usually deserves extra attention."
            ),
            suggested_next_steps=[
                "Consider listing each debt balance, interest rate, minimum payment, and due date.",
                "You may want to research how high-interest debt compares with your cash buffer.",
                "Review whether extra payments would reduce flexibility too much before changing anything.",
            ],
        )

    if intent == "retirement":
        return IntentAnswer(
            summary="Retirement accounts are long-term wealth buckets with special tax and contribution rules.",
            beginner_explanation=(
                "The first beginner-friendly retirement concept is employer match: if available, it is "
                "part of your compensation, but the plan rules and vesting schedule matter."
            ),
            suggested_next_steps=[
                "Consider reviewing whether your employer offers a match and how the formula works.",
                "You may want to research the investment mix inside the retirement account.",
                "Review contribution assumptions before comparing retirement scenarios.",
            ],
        )

    if intent == "tax":
        return IntentAnswer(
            summary="Taxes can change the real result of investing decisions, especially when selling assets.",
            beginner_explanation=(
                "Short-term and long-term holding periods can be treated differently for taxes. CrocLens "
                "keeps this educational and does not replace tax advice."
            ),
            suggested_next_steps=[
                "Consider reviewing purchase dates and cost basis before selling taxable investments.",
                "You may want to research capital gains, losses, and wash-sale basics.",
                "This may be worth discussing with a tax professional for your specific situation.",
            ],
        )

    if intent == "market":
        return IntentAnswer(
            summary="Market moves matter most when they affect assets that are a meaningful share of your wealth.",
            beginner_explanation=(
                "A big headline may not affect everyone the same way. CrocLens looks at what you own, "
                "how large each position is, and whether the impact is short-term noise or long-term risk."
            ),
            suggested_next_steps=[
                "Consider checking which holdings are actually connected to the market event.",
                "You may want to compare short-term price movement with your long-term goal.",
                "Check the data freshness label before relying on market context.",
            ],
        )

    if intent == "risk":
        return IntentAnswer(
            summary="Risk is not one number; it includes volatility, concentration, liquidity, debt, and taxes.",
            beginner_explanation=(
                "For beginners, the most useful risk question is often: could this surprise force me to "
                "change plans at a bad time?"
            ),
            suggested_next_steps=[
                "Consider reviewing your largest asset classes and whether one area dominates.",
                "You may want to compare liquid assets with debts and emergency cash needs.",
                "Review whether your risk profile matches your time horizon.",
            ],
        )

    if intent == "education":
        return IntentAnswer(
            summary="I can explain money concepts in plain language using your CrocLens sample context.",
            beginner_explanation=(
                "A useful way to learn is to connect each concept to the dashboard: assets are what you own, "
                "liabilities are what you owe, and net worth is the difference."
            ),
            suggested_next_steps=[
                "Consider asking about one metric at a time, such as liquidity or diversification.",
                "You may want to compare the explanation with the matching dashboard card.",
                "Review the source and data limitation labels so you know what is sample data.",
            ],
        )

    return IntentAnswer(
        summary="Croc Guide can help explain this using your sample whole-wealth dashboard data.",
        beginner_explanation=(
            "Based on the data provided, the biggest beginner-friendly idea is to compare risk, liquidity, "
            "debt, and diversification together instead of looking at one asset alone."
        ),
        suggested_next_steps=[
            "Consider reviewing your asset allocation before focusing on any single holding.",
            "You may want to research how higher-interest debt affects net worth.",
            "Check the data freshness label before relying on any market movement.",
        ],
    )


def answer_question(request: AssistantRequest) -> AssistantResponse:
    question = normalize_question(request.question)
    intent = route_intent(question)
    safety = run_safety_check(question)
    prompt_context = build_prompt_context(question, intent)
    intent_answer = answer_for_intent(intent, question, request.beginner_mode)

    limitations = [
        "This response uses CrocLens sample data, not live financial accounts.",
        "No live market data, tax lots, legal context, or account aggregation is connected yet.",
        f"Question received: {question}",
    ]

    if not safety.passed:
        limitations.insert(0, "The question included wording that CrocLens treats as unsafe for direct financial advice.")

    return AssistantResponse(
        intent=intent,
        summary=intent_answer.summary,
        beginner_explanation=intent_answer.beginner_explanation,
        suggested_next_steps=intent_answer.suggested_next_steps,
        confidence="medium",
        data_limitations=limitations,
        sources=[MOCK_SOURCE],
        safety=safety,
        prompt_context=prompt_context if request.include_prompt_debug else None,
        safety_disclaimer=EDUCATIONAL_DISCLAIMER,
    )
