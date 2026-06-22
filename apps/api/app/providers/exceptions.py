class ProviderError(RuntimeError):
    """Base class for normalized external provider failures."""

    code = "provider_error"


class ProviderUnavailableError(ProviderError):
    code = "provider_unavailable"


class ProviderTimeoutError(ProviderError):
    code = "provider_timeout"


class ProviderRateLimitError(ProviderError):
    code = "provider_rate_limited"


class ProviderInvalidSymbolError(ProviderError):
    code = "provider_invalid_symbol"


class ProviderMalformedResponseError(ProviderError):
    code = "provider_malformed_response"


class ProviderCapabilityError(ProviderError):
    code = "provider_capability_not_supported"
