from app.agents.schemas import AgentResult, AgentTrace


class ActionPlanAgent:
    agent_name = "action_plan"

    def build(self, specialist_result: AgentResult) -> tuple[list[str], AgentTrace]:
        action_items = [
            item if item.lower().startswith(("consider", "review", "research", "compare", "discuss"))
            else f"Consider {item[0].lower()}{item[1:]}"
            for item in specialist_result.action_items
        ]
        return action_items, AgentTrace(
            agent="action_plan",
            status="used",
            input_summary=specialist_result.summary,
            output_summary="Converted specialist output into safe beginner next steps.",
            tools_used=[],
        )
