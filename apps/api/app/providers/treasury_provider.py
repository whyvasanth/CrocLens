from app.providers.base import BaseProvider, ProviderRuntimeConfig


class TreasuryProvider(BaseProvider):
    name = "treasury"
    display_name = "U.S. Treasury and Fiscal Data"
    capabilities = ("treasury_rates",)

    def __init__(self, *, enabled: bool, config: ProviderRuntimeConfig) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "Treasury and Fiscal Data endpoints are public official data sources.",
                "Rate datasets may publish on a schedule and should not be labeled real-time.",
                "Phase 21A only registers the provider; live retrieval comes in Phase 21B.",
            ],
        )
