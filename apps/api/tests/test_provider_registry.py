import pytest

from app.providers.exceptions import ProviderCapabilityError
from app.providers.registry import build_default_provider_registry


@pytest.mark.anyio
async def test_default_provider_registry_reports_free_first_providers() -> None:
    registry = build_default_provider_registry()
    status = await registry.status()
    provider_names = {provider.provider_name for provider in status.providers}

    assert status.mode == "foundation"
    assert provider_names == {"yfinance", "coingecko", "fred", "treasury", "sec_edgar"}
    assert "Provider failures must never be silently relabeled" in status.data_limitations[1]
    assert all(provider.cache_ttl_seconds >= 0 for provider in status.providers)
    assert all(provider.stale_after_seconds >= 0 for provider in status.providers)


@pytest.mark.anyio
async def test_provider_registry_routes_by_capability_without_network_calls() -> None:
    registry = build_default_provider_registry()

    quote_providers = registry.providers_for("quote")
    crypto_providers = registry.providers_for("crypto_price")
    filings_providers = registry.providers_for("sec_filings")

    assert [provider.name for provider in quote_providers] == ["yfinance"]
    assert [provider.name for provider in crypto_providers] == ["coingecko"]
    assert filings_providers == []


@pytest.mark.anyio
async def test_sec_provider_requires_user_agent_before_filings_are_routable() -> None:
    registry = build_default_provider_registry()
    sec_health = await registry.health_for_provider("sec_edgar")

    assert sec_health is not None
    assert sec_health.provider_status == "not_configured"
    assert sec_health.configured is False
    assert "User-Agent" in sec_health.data_limitations[1]


@pytest.mark.anyio
async def test_unsupported_provider_operation_raises_normalized_exception() -> None:
    registry = build_default_provider_registry()
    yfinance_provider = registry.providers["yfinance"]

    with pytest.raises(ProviderCapabilityError):
        await yfinance_provider.get_filings("VTI")
