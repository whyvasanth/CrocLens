from app.providers.base import BaseProvider, ProviderRuntimeConfig


class YFinanceProvider(BaseProvider):
    name = "yfinance"
    display_name = "Yahoo Finance via yfinance"
    capabilities = ("quote", "history", "profile", "dividends", "splits")

    def __init__(self, *, enabled: bool, config: ProviderRuntimeConfig) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "yfinance is an unofficial third-party wrapper around Yahoo Finance data.",
                "Market data may be delayed, incomplete, adjusted, or unavailable.",
                "CrocLens will label this data as educational context, not real-time trading data.",
            ],
        )
