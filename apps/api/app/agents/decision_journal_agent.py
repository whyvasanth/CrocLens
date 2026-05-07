from app.agents.base import BaseAgent
from app.agents.schemas import AgentDataSource, AgentRequest, AgentResult, AgentTrace


class DecisionJournalAgent(BaseAgent):
    agent_name = "decision_journal"

    def run(self, request: AgentRequest, context: dict) -> AgentResult:
        return AgentResult(
            agent="decision_journal",
            summary="Decision journal feedback should compare your reason, expected outcome, risk considered, and review date.",
            reasoning_summary="The journal creates a learning loop without judging decisions as right or wrong too early.",
            action_items=[
                "Write the reason for the decision before acting.",
                "Record the risk you considered and what would change your mind.",
                "Set a review date so you can learn from the outcome later.",
            ],
            risks=["Feedback can be misleading if the original reason or review date is missing."],
            confidence="medium",
            data_sources=[
                AgentDataSource(
                    provider="croclens_sample_journal",
                    label="Sample decision journal context",
                    freshness="sample",
                    as_of="2026-05-05",
                    limitations=["Sample journal data only."],
                )
            ],
            data_freshness="sample",
            limitations=["Journal feedback is educational process feedback, not advice to trade."],
            trace=AgentTrace(
                agent="decision_journal",
                status="used",
                input_summary="Decision journal context.",
                output_summary="Generated decision feedback framework.",
                tools_used=["decision_journal_entries"],
            ),
        )
