from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
import json

from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.errors import ProviderUnavailableError
from app.data_providers.schemas import NormalizedDataPoint


class TreasuryProvider(BaseDataProvider):
    provider_id = "treasury_fiscal_data"
    display_name = "Treasury Fiscal Data"
    source_type = "official_treasury_data"
    capabilities = ["treasury_rates"]
    requires_api_key = False
    cost_note = "Free official U.S. government API."
    limitations = [
        "Treasury data is public macro context and may update after market hours.",
        "This endpoint does not provide stock, ETF, mutual fund, or crypto prices.",
    ]

    def get_treasury_rates(self) -> NormalizedDataPoint:
        params = urlencode({"sort": "-record_date", "page[size]": "1"})
        url = (
            "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/"
            f"accounting/od/avg_interest_rates?{params}"
        )

        try:
            with urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ProviderUnavailableError(f"Treasury Fiscal Data lookup failed: {exc}") from exc

        records = payload.get("data") or []
        if not records:
            raise ProviderUnavailableError("Treasury Fiscal Data returned no average interest rate records.")

        latest = records[0]
        value_text = latest.get("avg_interest_rate_amt")
        if value_text is None:
            raise ProviderUnavailableError("Treasury Fiscal Data did not include avg_interest_rate_amt.")

        return NormalizedDataPoint(
            provider=self.provider_id,
            source_type="treasury_rates",
            asset_type="treasury",
            symbol_or_series_id="AVG_INTEREST_RATE",
            value=float(value_text),
            currency=None,
            as_of=datetime.fromisoformat(latest["record_date"]).replace(tzinfo=utc_now().tzinfo),
            retrieved_at=utc_now(),
            source_url=url,
            freshness="official Treasury Fiscal Data latest available record",
            confidence="high",
            limitations=self.limitations,
            raw_payload=latest,
        )
