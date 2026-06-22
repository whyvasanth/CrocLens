from app.providers.base import BaseProvider, ProviderRuntimeConfig


class CoinGeckoProvider(BaseProvider):
    name = "coingecko"
    display_name = "CoinGecko public crypto API"
    capabilities = ("crypto_price", "history")

    def __init__(self, *, enabled: bool, config: ProviderRuntimeConfig) -> None:
        super().__init__(
            enabled=enabled,
            configured=True,
            config=config,
            data_limitations=[
                "CoinGecko public endpoints are rate limited and may be unavailable during local testing.",
                "Crypto prices are volatile and may not be real-time.",
                "Only a small allowlisted set of common crypto identifiers should be supported in the MVP.",
            ],
        )
