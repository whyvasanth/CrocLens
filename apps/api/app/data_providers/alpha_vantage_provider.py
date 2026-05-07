from app.core.config import settings
from app.data_providers.base import BaseDataProvider


class AlphaVantageProvider(BaseDataProvider):
    provider_id = "alpha_vantage"
    display_name = "Alpha Vantage"
    source_type = "optional_market_data_backup"
    capabilities = ["market_price", "price_history", "technical_indicators"]
    requires_api_key = True
    cost_note = "Free tier is limited; optional backup only."
    limitations = [
        "Free-tier rate limits are low.",
        "CrocLens must fall back to sample data when this key is absent or rate-limited.",
    ]

    def is_configured(self) -> bool:
        return bool(settings.alpha_vantage_api_key)
