from app.data_providers.base import BaseDataProvider


class FhfaProvider(BaseDataProvider):
    provider_id = "fhfa"
    display_name = "FHFA housing data"
    source_type = "official_housing_data"
    capabilities = ["housing_index"]
    requires_api_key = False
    cost_note = "Free official housing market source."
    limitations = [
        "FHFA HPI is regional housing context, not an exact home valuation.",
        "Property-specific estimates still require manual entry or professional valuation.",
    ]
