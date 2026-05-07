from app.agents.router_agent import UNSAFE_TERMS
from app.agents.schemas import FinalAIResponse, AgentRequest, AgentTrace
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


BLOCKED_OUTPUT_TERMS = [
    "buy this",
    "sell this",
    "guaranteed return",
    "will make money",
    "best investment",
]


class SafetyGuardrailAgent:
    agent_name = "safety_guardrail"

    def review(self, request: AgentRequest, response: FinalAIResponse) -> FinalAIResponse:
        lowered_question = request.question.lower()
        lowered_output = " ".join(
            [response.summary, response.reasoning_summary, *response.action_items, *response.risks]
        ).lower()
        flags = [term for term in UNSAFE_TERMS if term in lowered_question]
        flags.extend(term for term in BLOCKED_OUTPUT_TERMS if term in lowered_output)

        if flags:
            response.summary = (
                "I can help you review this safely, but I cannot tell you to buy or sell anything "
                "or provide direct trading advice."
            )
            response.reasoning_summary = (
                "The request or draft response included wording CrocLens treats as unsafe. "
                "The response was reframed into educational review language."
            )
            response.action_items = [
                "Consider reviewing how the idea fits your goals, time horizon, and risk comfort.",
                "Research the asset, fees, taxes, liquidity, and downside scenarios.",
                "Discuss personalized financial or tax decisions with a qualified professional.",
            ]
            response.confidence = "low"

        response.safety_flags = sorted(set(flags))
        response.safety_disclaimer = EDUCATIONAL_DISCLAIMER
        response.agent_trace.append(
            AgentTrace(
                agent="safety_guardrail",
                status="used",
                input_summary="Draft AI response and original user request.",
                output_summary="Validated safe wording, limitations, confidence, and disclaimer.",
                tools_used=["unsafe_language_rules", "prompt_injection_rules"],
            )
        )
        if "This is educational, not financial advice." not in response.limitations:
            response.limitations.append("This is educational, not financial advice.")
        return response
