from datetime import UTC, datetime
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

from app.core.config import settings
from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.errors import ProviderUnavailableError
from app.data_providers.schemas import NormalizedDataPoint


class CoinGeckoProvider(BaseDataProvider):
    provider_id = "coingecko"
    display_name = "CoinGecko public crypto API"
    source_type = "crypto_market_data"
    capabilities = ["crypto_price"]
    requires_api_key = False
    cost_note = "Public/demo endpoints are available with rate limits; no subscription is required for MVP fallback mode."
    limitations = [
        "CoinGecko public endpoints can be rate-limited or delayed.",
        "Crypto prices are volatile and should be treated as educational context only.",
    ]

    def get_crypto_price(self, coin_id: str) -> NormalizedDataPoint:
        safe_coin = quote(coin_id.lower())
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={safe_coin}&vs_currencies=usd&include_last_updated_at=true"
        )
        headers = {"Accept": "application/json"}
        if settings.coingecko_api_key:
            headers["x-cg-demo-api-key"] = settings.coingecko_api_key

        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ProviderUnavailableError(f"CoinGecko lookup failed for {coin_id}: {exc}") from exc

        coin_payload = payload.get(coin_id.lower())
        if not coin_payload or "usd" not in coin_payload:
            raise ProviderUnavailableError(f"CoinGecko returned no USD price for {coin_id}.")

        last_updated_at = coin_payload.get("last_updated_at")
        as_of = (
            datetime.fromtimestamp(last_updated_at, tz=UTC)
            if isinstance(last_updated_at, int)
            else utc_now()
        )

        return NormalizedDataPoint(
            provider=self.provider_id,
            source_type="crypto_price",
            asset_type="crypto",
            symbol_or_series_id=coin_id.lower(),
            value=float(coin_payload["usd"]),
            currency="USD",
            as_of=as_of,
            retrieved_at=utc_now(),
            source_url=f"https://www.coingecko.com/en/coins/{coin_id.lower()}",
            freshness="public crypto quote; verify rate limits and freshness before relying on it",
            confidence="medium",
            limitations=self.limitations,
            raw_payload=coin_payload,
        )
