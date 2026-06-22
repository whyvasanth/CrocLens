from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Asset, Holding, MarketPrice, Portfolio, PortfolioNetWorthSnapshot, ProviderError, ProviderIngestionRun, User
from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderUnavailableError
from app.providers.models import MarketQuote, utc_now
from app.services.market_data_cache_service import (
    capture_net_worth_snapshot,
    get_or_refresh_quote,
    refresh_user_public_holding_prices,
)


class FakeQuoteProvider(BaseProvider):
    name = "fake_quote_provider"
    display_name = "Fake quote provider"
    capabilities = ("quote",)

    def __init__(self, *, price: Decimal | None = Decimal("250.00"), fail: bool = False, stale_after_seconds: int = 900) -> None:
        super().__init__(
            enabled=True,
            configured=True,
            config=ProviderRuntimeConfig(
                timeout_seconds=5,
                retry_limit=1,
                cache_ttl_seconds=300,
                stale_after_seconds=stale_after_seconds,
                user_agent="CrocLens tests",
            ),
            data_limitations=["Fake provider used only in tests."],
        )
        self.price = price
        self.fail = fail
        self.calls = 0

    async def get_quote(self, symbol: str) -> MarketQuote:
        self.calls += 1
        if self.fail:
            raise ProviderUnavailableError("Provider is intentionally unavailable.")
        return MarketQuote(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol.upper(),
            asset_type="etf",
            price=self.price,
            currency="USD",
            data_as_of=utc_now(),
            retrieved_at=utc_now(),
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://example.test/{symbol}",
            data_limitations=["Fake provider used only in tests."],
        )


@pytest.mark.anyio
async def test_quote_refresh_persists_once_and_reuses_fresh_cache() -> None:
    with SessionLocal() as db:
        user, asset, _holding = _create_user_holding(db)
        provider = FakeQuoteProvider()

        first = await get_or_refresh_quote(db, asset, provider)
        second = await get_or_refresh_quote(db, asset, provider)
        prices = list(db.scalars(select(MarketPrice).where(MarketPrice.asset_id == asset.id)))

        assert user.email.endswith("@example.com")
        assert first.status == "refreshed"
        assert second.status == "fresh_cache"
        assert provider.calls == 1
        assert len(prices) == 1
        assert prices[0].close_price == Decimal("250.000000")
        assert prices[0].is_sample_data is False
        assert prices[0].data_quality == "delayed"


@pytest.mark.anyio
async def test_quote_refresh_returns_stale_cache_when_provider_fails() -> None:
    with SessionLocal() as db:
        _user, asset, _holding = _create_user_holding(db)
        stale_price = MarketPrice(
            id=str(uuid4()),
            asset_id=asset.id,
            price_date=utc_now().date(),
            close_price=Decimal("200.00"),
            source_name="fake_quote_provider",
            currency="USD",
            data_as_of=utc_now() - timedelta(hours=2),
            retrieved_at=utc_now() - timedelta(hours=2),
            provider_status="healthy",
            data_quality="delayed",
            is_stale=False,
            is_sample_data=False,
            data_limitations=[],
            raw_response_metadata={},
        )
        db.add(stale_price)
        db.flush()
        provider = FakeQuoteProvider(fail=True, stale_after_seconds=60)

        result = await get_or_refresh_quote(db, asset, provider)
        errors = list(db.scalars(select(ProviderError)))
        runs = list(db.scalars(select(ProviderIngestionRun)))

        assert result.status == "stale_cache"
        assert result.price is stale_price
        assert result.warning is not None
        assert stale_price.is_stale is True
        assert errors[0].error_code == "provider_unavailable"
        assert runs[0].status == "failed"


@pytest.mark.anyio
async def test_quote_refresh_is_unavailable_without_cached_data() -> None:
    with SessionLocal() as db:
        _user, asset, _holding = _create_user_holding(db)
        provider = FakeQuoteProvider(fail=True)

        result = await get_or_refresh_quote(db, asset, provider)

        assert result.status == "unavailable"
        assert result.price is None
        assert "no stored observation" in (result.warning or "")
        assert db.scalar(select(ProviderError)) is not None


@pytest.mark.anyio
async def test_refresh_user_public_holding_prices_updates_quantity_based_value() -> None:
    with SessionLocal() as db:
        user, _asset, holding = _create_user_holding(db, quantity=Decimal("5"), market_value=Decimal("100.00"))
        provider = FakeQuoteProvider(price=Decimal("251.25"))

        counts = await refresh_user_public_holding_prices(db, user, provider)

        assert counts["refreshed"] == 1
        assert holding.market_value == Decimal("1256.25")


def test_capture_net_worth_snapshot_is_idempotent_per_day() -> None:
    with SessionLocal() as db:
        user, _asset, _holding = _create_user_holding(db, quantity=Decimal("1"), market_value=Decimal("500.00"))

        first = capture_net_worth_snapshot(db, user)
        second = capture_net_worth_snapshot(db, user)
        snapshots = list(db.scalars(select(PortfolioNetWorthSnapshot)))

        assert first.id == second.id
        assert len(snapshots) == 1
        assert snapshots[0].total_assets == Decimal("500.00")
        assert snapshots[0].net_worth == Decimal("500.00")


def _create_user_holding(
    db,
    *,
    quantity: Decimal = Decimal("1"),
    market_value: Decimal = Decimal("250.00"),
) -> tuple[User, Asset, Holding]:
    user = User(
        id=str(uuid4()),
        email=f"{uuid4()}@example.com",
        full_name="Owner",
        status="active",
        auth_provider="local",
    )
    portfolio = Portfolio(
        id=str(uuid4()),
        user=user,
        name="Test portfolio",
        base_currency="USD",
    )
    asset = Asset(
        id=str(uuid4()),
        symbol="VTI",
        name="Total Stock Market ETF",
        asset_type="ETFs",
        currency="USD",
        data_source="manual_entry",
    )
    holding = Holding(
        id=str(uuid4()),
        portfolio=portfolio,
        asset=asset,
        quantity=quantity,
        market_value=market_value,
    )
    db.add_all([user, portfolio, asset, holding])
    db.flush()
    return user, asset, holding
