from app.core.config import settings
from app.data_providers.base import BaseDataProvider


class SecEdgarProvider(BaseDataProvider):
    provider_id = "sec_edgar"
    display_name = "SEC EDGAR"
    source_type = "official_company_filings"
    capabilities = ["company_filings", "company_profile"]
    requires_api_key = False
    cost_note = "Free official SEC source; requires responsible User-Agent configuration."
    limitations = [
        "SEC filings are official but can be complex and delayed.",
        "CrocLens should summarize filings educationally and avoid investment recommendations.",
    ]

    def is_configured(self) -> bool:
        return bool(settings.sec_edgar_user_agent)
