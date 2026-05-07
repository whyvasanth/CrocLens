class DataProviderError(RuntimeError):
    """Base error for provider failures that should be safe to show as limitations."""


class ProviderUnavailableError(DataProviderError):
    """Raised when a provider cannot be reached or a dependency is unavailable."""


class ProviderConfigurationError(DataProviderError):
    """Raised when a provider needs configuration that is missing locally."""


class CapabilityNotSupportedError(DataProviderError):
    """Raised when a provider does not support the requested capability."""
