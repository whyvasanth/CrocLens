from app.providers.base import BaseProvider, ProviderRuntimeConfig


class SecProvider(BaseProvider):
    name = "sec_edgar"
    display_name = "SEC EDGAR"
    capabilities = ("profile", "sec_filings")

    def __init__(self, *, enabled: bool, user_agent: str, config: ProviderRuntimeConfig) -> None:
        super().__init__(
            enabled=enabled,
            configured=bool(user_agent.strip()),
            config=config,
            data_limitations=[
                "SEC EDGAR is official for filings, not market prices.",
                "SEC requests require a descriptive User-Agent identifying the application/contact.",
                "Company filing data may lag company events and should be used as research context.",
            ],
        )
