from app.schemas.api import EvaluationMetricResponse, EvaluationMetricsResponse, SourceMetadata

EVALUATION_SOURCE = SourceMetadata(
    name="CrocLens local evaluation fixture",
    freshness="Static sample metrics for Phase 19",
    as_of="2026-05-06",
)

EDUCATIONAL_DISCLAIMER = (
    "CrocLens metrics are for product quality and safety evaluation. This is educational software, "
    "not financial advice."
)


def get_evaluation_metrics() -> EvaluationMetricsResponse:
    metrics = [
        EvaluationMetricResponse(
            id="onboarding_completion_rate",
            label="Onboarding completion",
            category="product",
            value=72.0,
            unit="percent",
            target="70% or higher",
            direction="higher_is_better",
            status="healthy",
            sample_size=50,
            beginner_explanation=(
                "This checks whether beginners can finish the first setup flow without getting stuck."
            ),
            how_measured="Completed onboarding profiles divided by started onboarding sessions.",
            limitations=[
                "Uses sample events until production analytics exists.",
                "Does not prove users understood every question.",
            ],
        ),
        EvaluationMetricResponse(
            id="portfolio_creation_rate",
            label="Portfolio creation",
            category="product",
            value=61.0,
            unit="percent",
            target="60% or higher",
            direction="higher_is_better",
            status="healthy",
            sample_size=50,
            beginner_explanation=(
                "This shows whether users can enter enough assets and debts to see a useful dashboard."
            ),
            how_measured="Users with at least one asset or liability divided by completed onboarding users.",
            limitations=[
                "Manual entry quality is not measured yet.",
                "Linked financial accounts are not supported in the MVP.",
            ],
        ),
        EvaluationMetricResponse(
            id="action_plan_usage_rate",
            label="Action plan usage",
            category="product",
            value=44.0,
            unit="percent",
            target="50% or higher",
            direction="higher_is_better",
            status="watch",
            sample_size=50,
            beginner_explanation=(
                "This checks whether users are finding the suggested educational next steps useful."
            ),
            how_measured="Users who opened or completed an action plan divided by active sample users.",
            limitations=[
                "Sample data cannot distinguish curiosity from genuine usefulness.",
                "Completion should later require a user-confirmed action, not just a click.",
            ],
        ),
        EvaluationMetricResponse(
            id="ai_clarity_score",
            label="AI clarity score",
            category="ai_safety",
            value=4.3,
            unit="out_of_5",
            target="4.2 out of 5 or higher",
            direction="higher_is_better",
            status="healthy",
            sample_size=25,
            beginner_explanation=(
                "This estimates whether Croc Guide explanations feel understandable to beginners."
            ),
            how_measured="Reviewer ratings for answer clarity on a 1 to 5 rubric.",
            limitations=[
                "Reviewer samples are small.",
                "Real user feedback is not collected yet.",
            ],
        ),
        EvaluationMetricResponse(
            id="hallucination_check_pass_rate",
            label="Hallucination checks",
            category="ai_safety",
            value=96.0,
            unit="percent",
            target="95% or higher",
            direction="higher_is_better",
            status="healthy",
            sample_size=25,
            beginner_explanation=(
                "This checks whether AI-style responses stay grounded in available sample data."
            ),
            how_measured="Evaluation prompts that avoid unsupported facts divided by prompts reviewed.",
            limitations=[
                "Rule-based responses are easier to control than future LLM responses.",
                "This does not replace human review for high-risk financial wording.",
            ],
        ),
        EvaluationMetricResponse(
            id="unsafe_recommendation_rate",
            label="Unsafe recommendation rate",
            category="ai_safety",
            value=0.0,
            unit="percent",
            target="Below 1%",
            direction="lower_is_better",
            status="healthy",
            sample_size=25,
            beginner_explanation=(
                "This measures whether CrocLens accidentally tells users to buy, sell, or expect guaranteed returns."
            ),
            how_measured="Unsafe AI outputs divided by evaluated AI outputs.",
            limitations=[
                "Current assistant is deterministic and rule-based.",
                "Future model-backed assistants need larger adversarial test sets.",
            ],
        ),
        EvaluationMetricResponse(
            id="data_freshness_coverage",
            label="Data freshness coverage",
            category="data_quality",
            value=83.0,
            unit="percent",
            target="90% or higher",
            direction="higher_is_better",
            status="watch",
            sample_size=6,
            beginner_explanation=(
                "This checks how often market, news, and portfolio facts show an as-of date or freshness label."
            ),
            how_measured="Records with freshness metadata divided by records shown in product surfaces.",
            limitations=[
                "Sample data uses static as-of dates.",
                "Live data freshness requires real ingestion jobs later.",
            ],
        ),
        EvaluationMetricResponse(
            id="median_api_latency_ms",
            label="Median API latency",
            category="reliability",
            value=142.0,
            unit="milliseconds",
            target="Below 300 ms",
            direction="lower_is_better",
            status="healthy",
            sample_size=100,
            beginner_explanation=(
                "This checks whether the app feels responsive when pages request backend data."
            ),
            how_measured="Median response time across local sample API requests.",
            limitations=[
                "Local latency does not predict real deployed latency.",
                "No production traffic exists yet.",
            ],
        ),
        EvaluationMetricResponse(
            id="api_error_rate",
            label="API error rate",
            category="reliability",
            value=0.8,
            unit="percent",
            target="Below 2%",
            direction="lower_is_better",
            status="healthy",
            sample_size=100,
            beginner_explanation=(
                "This checks how often API calls fail in a way that users would notice."
            ),
            how_measured="5xx and unexpected failed responses divided by total local sample requests.",
            limitations=[
                "Does not include browser network failures.",
                "Production should separate user errors, service errors, and provider errors.",
            ],
        ),
    ]

    return EvaluationMetricsResponse(
        headline="CrocLens is tracking product usefulness, AI safety, data quality, and reliability.",
        beginner_summary=(
            "Think of this as a scorecard for the product itself. It helps us see whether CrocLens is clear, "
            "safe, useful, and technically dependable before adding more advanced AI or live data."
        ),
        metrics=metrics,
        quality_checks=[
            "Every AI output should include confidence, limitations, sources, and safe wording.",
            "Every data-driven surface should show freshness or a sample-data label.",
            "Every metric should have a target and a clear definition before it is used for decisions.",
            "No paid analytics, paid monitoring, or external tracking tools are required for the MVP.",
        ],
        recommended_reviews=[
            "Review action plan usage because it is below the target.",
            "Improve freshness labels before adding more live data sources.",
            "Expand adversarial AI safety tests before connecting a real LLM.",
        ],
        confidence="medium",
        data_limitations=[
            "Phase 19 metrics are deterministic sample metrics, not real user analytics.",
            "Production metrics should be calculated from privacy-aware event logs and observability data.",
            "User-level analytics should stay opt-in and should avoid storing sensitive financial details.",
        ],
        sources=[EVALUATION_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )
