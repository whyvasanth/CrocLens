import os
from dataclasses import dataclass, field


def _getenv(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _getenv_int(name: str, default: int) -> int:
    raw_value = _getenv(name, str(default))
    try:
        return int(raw_value)
    except ValueError:
        return default


def _getenv_bool(name: str, default: bool) -> bool:
    raw_value = _getenv(name, str(default)).lower()
    return raw_value in {"1", "true", "yes", "on"}


def _getenv_list(name: str, default: list[str]) -> list[str]:
    raw_value = _getenv(name)
    if not raw_value:
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    api_prefix: str = "/api/v1"
    api_version: str = "0.1.0"
    app_env: str = _getenv("APP_ENV", "local")
    auth_mode: str = _getenv("AUTH_MODE", "local")
    aws_region: str = _getenv("AWS_REGION", "us-east-1")
    cognito_user_pool_id: str = _getenv("COGNITO_USER_POOL_ID")
    cognito_app_client_id: str = _getenv("COGNITO_APP_CLIENT_ID")
    cognito_domain: str = _getenv("COGNITO_DOMAIN")
    market_data_provider: str = _getenv("MARKET_DATA_PROVIDER", "yfinance")
    market_data_cache_seconds: int = _getenv_int("MARKET_DATA_CACHE_SECONDS", 300)
    rate_limit_per_minute: int = _getenv_int("RATE_LIMIT_PER_MINUTE", 300)
    demo_mode_enabled: bool = _getenv_bool("DEMO_MODE_ENABLED", True)
    log_level: str = _getenv("LOG_LEVEL", "INFO").upper()
    market_provider_mode: str = _getenv("MARKET_PROVIDER_MODE", "mock_or_live")
    market_provider_timeout_seconds: int = _getenv_int("MARKET_PROVIDER_TIMEOUT_SECONDS", 10)
    market_provider_retry_limit: int = _getenv_int("MARKET_PROVIDER_RETRY_LIMIT", 2)
    market_provider_cache_ttl_seconds: int = _getenv_int(
        "MARKET_PROVIDER_CACHE_TTL_SECONDS",
        _getenv_int("MARKET_DATA_CACHE_SECONDS", 300),
    )
    market_provider_stale_after_seconds: int = _getenv_int("MARKET_PROVIDER_STALE_AFTER_SECONDS", 900)
    market_provider_user_agent: str = _getenv("MARKET_PROVIDER_USER_AGENT", "CrocLens local development")
    enable_yfinance_provider: bool = _getenv_bool("ENABLE_YFINANCE_PROVIDER", True)
    enable_coingecko_provider: bool = _getenv_bool("ENABLE_COINGECKO_PROVIDER", True)
    enable_fred_provider: bool = _getenv_bool("ENABLE_FRED_PROVIDER", True)
    enable_treasury_provider: bool = _getenv_bool("ENABLE_TREASURY_PROVIDER", True)
    enable_sec_provider: bool = _getenv_bool("ENABLE_SEC_PROVIDER", True)
    sec_edgar_user_agent: str = _getenv("SEC_EDGAR_USER_AGENT")
    database_url: str = _getenv(
        "DATABASE_URL",
        "sqlite:///./croclens-local.db"
        if _getenv("APP_ENV", "local") == "test"
        else "postgresql+psycopg://croclens:croclens@localhost:55432/croclens",
    )
    cors_origins: list[str] = field(
        default_factory=lambda: _getenv_list(
            "CORS_ORIGINS",
            [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ],
        )
    )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_local_auth_enabled(self) -> bool:
        return self.auth_mode == "local" and not self.is_production


settings = Settings()
