from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    api_prefix: str = "/api/v1"
    api_version: str = "0.1.0"
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )


settings = Settings()

