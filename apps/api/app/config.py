import os


class Settings:
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    yfinance_timeout_seconds: int = int(os.getenv("YFINANCE_TIMEOUT_SECONDS", "12"))


settings = Settings()
