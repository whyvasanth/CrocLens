import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    api_prefix: str = "/api/v1"
    api_version: str = "0.1.0"
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "300"))
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    fred_api_key: str = os.getenv("FRED_API_KEY", "")
    coingecko_api_key: str = os.getenv("COINGECKO_API_KEY", "")
    openfigi_api_key: str = os.getenv("OPENFIGI_API_KEY", "")
    census_api_key: str = os.getenv("CENSUS_API_KEY", "")
    sec_edgar_user_agent: str = os.getenv("SEC_EDGAR_USER_AGENT", "")
    data_provider_mode: str = os.getenv("DATA_PROVIDER_MODE", "mock_or_live")
    data_cache_ttl_seconds: int = int(os.getenv("DATA_CACHE_TTL_SECONDS", "300"))
    llm_mode: str = os.getenv("LLM_MODE", "mock")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://croclens:croclens@localhost:5432/croclens",
    )
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
    )


settings = Settings()
