from app.core.config import settings
from app.data_providers.base import BaseDataProvider


class OpenFigiProvider(BaseDataProvider):
    provider_id = "openfigi"
    display_name = "OpenFIGI"
    source_type = "security_identifier_mapping"
    capabilities = ["security_mapping"]
    requires_api_key = False
    cost_note = "Free identifier mapping with optional API key for higher limits."
    limitations = [
        "OpenFIGI maps identifiers and is not a market price source.",
        "Mappings should be reviewed when symbols are ambiguous.",
    ]

    def is_configured(self) -> bool:
        return True if settings.openfigi_api_key or not self.requires_api_key else False
