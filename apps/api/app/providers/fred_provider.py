from app.providers.base import BaseProvider, ProviderRuntimeConfig


class FredProvider(BaseProvider):
    name = "fred"
    display_name = "FRED public CSV data"
    capabilities = ("macro_series", "treasury_rates")

    def __init__(self, *, enabled: bool, config: ProviderRuntimeConfig) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "FRED macroeconomic observations may be delayed or revised.",
                "Phase 21A only registers the provider; no live macro requests are made yet.",
                "CrocLens must show observation dates and revisions when macro data is later displayed.",
            ],
        )
