from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(40), default="local", nullable=False)
    external_auth_subject: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))

    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    portfolios: Mapped[list["Portfolio"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    local_sessions: Mapped[list["LocalAuthSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class LocalAuthSession(TimestampMixin, Base):
    __tablename__ = "local_auth_sessions"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_local_auth_sessions_token_hash"),
        Index("ix_local_auth_sessions_user_expires", "user_id", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="local_sessions")


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    beginner_mode: Mapped[bool] = mapped_column(default=True, nullable=False)
    risk_tolerance: Mapped[str | None] = mapped_column(String(40))
    time_horizon: Mapped[str | None] = mapped_column(String(80))
    primary_goal: Mapped[str | None] = mapped_column(String(160))
    household_income_range: Mapped[str | None] = mapped_column(String(80))

    user: Mapped["User"] = relationship(back_populates="profile")


class Portfolio(TimestampMixin, Base):
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    user: Mapped["User"] = relationship(back_populates="portfolios")
    holdings: Mapped[list["Holding"]] = relationship(back_populates="portfolio")


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("symbol", "asset_type", name="uq_assets_symbol_asset_type"),
        Index("ix_assets_asset_type_symbol", "asset_type", "symbol"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    data_source: Mapped[str | None] = mapped_column(String(120))

    holdings: Mapped[list["Holding"]] = relationship(back_populates="asset")


class Holding(TimestampMixin, Base):
    __tablename__ = "holdings"
    __table_args__ = (Index("ix_holdings_portfolio_asset", "portfolio_id", "asset_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    portfolio_id: Mapped[str] = mapped_column(ForeignKey("portfolios.id"), nullable=False)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), nullable=False)
    account_name: Mapped[str | None] = mapped_column(String(120))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=0, nullable=False)
    cost_basis: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    market_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    as_of_date: Mapped[date | None] = mapped_column(Date)

    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")
    asset: Mapped["Asset"] = relationship(back_populates="holdings")


class Liability(TimestampMixin, Base):
    __tablename__ = "liabilities"
    __table_args__ = (Index("ix_liabilities_user_type", "user_id", "liability_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    liability_type: Mapped[str] = mapped_column(String(60), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    interest_rate: Mapped[Decimal | None] = mapped_column(Numeric(7, 4))
    minimum_payment: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    due_day: Mapped[int | None]


class RealEstateProperty(TimestampMixin, Base):
    __tablename__ = "real_estate_properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(160), nullable=False)
    property_type: Mapped[str] = mapped_column(String(80), nullable=False)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    mortgage_balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    ownership_percent: Mapped[Decimal] = mapped_column(Numeric(6, 3), default=100, nullable=False)
    location_label: Mapped[str | None] = mapped_column(String(160))


class RetirementAccount(TimestampMixin, Base):
    __tablename__ = "retirement_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    account_type: Mapped[str] = mapped_column(String(60), nullable=False)
    provider_name: Mapped[str | None] = mapped_column(String(160))
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    contribution_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    employer_match_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))


class DecisionJournalEntry(TimestampMixin, Base):
    __tablename__ = "decision_journal_entries"
    __table_args__ = (Index("ix_decision_journal_user_review_date", "user_id", "review_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str | None] = mapped_column(Text)
    risk_considered: Mapped[str | None] = mapped_column(Text)
    review_date: Mapped[date | None] = mapped_column(Date)


class ActionPlan(TimestampMixin, Base):
    __tablename__ = "action_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="suggested", nullable=False)
    priority: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    data_limitations: Mapped[dict] = mapped_column(JSON_TYPE, default=list, nullable=False)


class AgentOutput(TimestampMixin, Base):
    __tablename__ = "agent_outputs"
    __table_args__ = (Index("ix_agent_outputs_user_agent", "user_id", "agent_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    intent: Mapped[str | None] = mapped_column(String(120))
    output_json: Mapped[dict] = mapped_column(JSON_TYPE, nullable=False)
    confidence: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    data_limitations: Mapped[dict] = mapped_column(JSON_TYPE, default=list, nullable=False)
    sources: Mapped[dict] = mapped_column(JSON_TYPE, default=list, nullable=False)
    safety_status: Mapped[str] = mapped_column(String(40), default="passed", nullable=False)


class MarketPrice(TimestampMixin, Base):
    __tablename__ = "market_prices"
    __table_args__ = (
        UniqueConstraint("asset_id", "price_date", "source_name", name="uq_market_prices_asset_date_source"),
        Index("ix_market_prices_asset_date", "asset_id", "price_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class NewsArticle(TimestampMixin, Base):
    __tablename__ = "news_articles"
    __table_args__ = (Index("ix_news_articles_published_at", "published_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)
    related_symbols: Mapped[dict] = mapped_column(JSON_TYPE, default=list, nullable=False)


class WatchlistItem(TimestampMixin, Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "asset_id", name="uq_watchlist_items_user_asset"),
        Index("ix_watchlist_items_user", "user_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class TaxLot(TimestampMixin, Base):
    __tablename__ = "tax_lots"
    __table_args__ = (Index("ix_tax_lots_holding_acquired", "holding_id", "acquired_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    holding_id: Mapped[str] = mapped_column(ForeignKey("holdings.id"), nullable=False)
    acquired_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    account_tax_type: Mapped[str] = mapped_column(String(60), default="taxable", nullable=False)


class AssetScore(TimestampMixin, Base):
    __tablename__ = "asset_scores"
    __table_args__ = (
        UniqueConstraint("asset_id", "score_date", name="uq_asset_scores_asset_date"),
        Index("ix_asset_scores_asset_date", "asset_id", "score_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), nullable=False)
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    risk_score: Mapped[int]
    liquidity_score: Mapped[int]
    diversification_score: Mapped[int]
    income_yield_score: Mapped[int]
    inflation_sensitivity_score: Mapped[int]
    tax_complexity_score: Mapped[int]
    methodology_version: Mapped[str] = mapped_column(String(40), default="phase_4_v1", nullable=False)
