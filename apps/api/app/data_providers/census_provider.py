from app.core.config import settings
from app.data_providers.base import BaseDataProvider


class CensusProvider(BaseDataProvider):
    provider_id = "census"
    display_name = "U.S. Census API"
    source_type = "official_local_context"
    capabilities = ["census_context"]
    requires_api_key = False
    cost_note = "Free public API; key can improve quota depending on endpoint."
    limitations = [
        "Census data is local context, not a personal affordability recommendation.",
        "Some endpoints may require or benefit from CENSUS_API_KEY.",
    ]

    def is_configured(self) -> bool:
        return True if settings.census_api_key or not self.requires_api_key else False
