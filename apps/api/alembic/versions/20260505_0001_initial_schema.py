"""create initial cross asset schema

Revision ID: 20260505_0001
Revises:
Create Date: 2026-05-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260505_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("symbol", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=60), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("data_source", sa.String(length=120), nullable=True),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assets")),
        sa.UniqueConstraint("symbol", "asset_type", name="uq_assets_symbol_asset_type"),
    )
    op.create_index(op.f("ix_assets_symbol"), "assets", ["symbol"], unique=False)
    op.create_index(op.f("ix_assets_asset_type"), "assets", ["asset_type"], unique=False)
    op.create_index("ix_assets_asset_type_symbol", "assets", ["asset_type", "symbol"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("beginner_mode", sa.Boolean(), nullable=False),
        sa.Column("risk_tolerance", sa.String(length=40), nullable=True),
        sa.Column("time_horizon", sa.String(length=80), nullable=True),
        sa.Column("primary_goal", sa.String(length=160), nullable=True),
        sa.Column("household_income_range", sa.String(length=80), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_profiles_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_profiles_user_id")),
    )

    op.create_table(
        "portfolios",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_portfolios_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_portfolios")),
    )
    op.create_index(op.f("ix_portfolios_user_id"), "portfolios", ["user_id"], unique=False)

    op.create_table(
        "holdings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("portfolio_id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("account_name", sa.String(length=120), nullable=True),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("cost_basis", sa.Numeric(18, 2), nullable=True),
        sa.Column("market_value", sa.Numeric(18, 2), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_holdings_asset_id_assets")),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], name=op.f("fk_holdings_portfolio_id_portfolios")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_holdings")),
    )
    op.create_index("ix_holdings_portfolio_asset", "holdings", ["portfolio_id", "asset_id"], unique=False)

    op.create_table(
        "liabilities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("liability_type", sa.String(length=60), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(7, 4), nullable=True),
        sa.Column("minimum_payment", sa.Numeric(18, 2), nullable=True),
        sa.Column("due_day", sa.Integer(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_liabilities_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_liabilities")),
    )
    op.create_index(op.f("ix_liabilities_user_id"), "liabilities", ["user_id"], unique=False)
    op.create_index("ix_liabilities_user_type", "liabilities", ["user_id", "liability_type"], unique=False)

    op.create_table(
        "real_estate_properties",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("nickname", sa.String(length=160), nullable=False),
        sa.Column("property_type", sa.String(length=80), nullable=False),
        sa.Column("estimated_value", sa.Numeric(18, 2), nullable=False),
        sa.Column("mortgage_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("ownership_percent", sa.Numeric(6, 3), nullable=False),
        sa.Column("location_label", sa.String(length=160), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_real_estate_properties_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_real_estate_properties")),
    )
    op.create_index(op.f("ix_real_estate_properties_user_id"), "real_estate_properties", ["user_id"], unique=False)

    op.create_table(
        "retirement_accounts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("account_type", sa.String(length=60), nullable=False),
        sa.Column("provider_name", sa.String(length=160), nullable=True),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False),
        sa.Column("contribution_percent", sa.Numeric(6, 3), nullable=True),
        sa.Column("employer_match_percent", sa.Numeric(6, 3), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_retirement_accounts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retirement_accounts")),
    )
    op.create_index(op.f("ix_retirement_accounts_user_id"), "retirement_accounts", ["user_id"], unique=False)

    op.create_table(
        "decision_journal_entries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("decision_type", sa.String(length=60), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("expected_outcome", sa.Text(), nullable=True),
        sa.Column("risk_considered", sa.Text(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_decision_journal_entries_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_decision_journal_entries")),
    )
    op.create_index(op.f("ix_decision_journal_entries_user_id"), "decision_journal_entries", ["user_id"], unique=False)
    op.create_index(
        "ix_decision_journal_user_review_date",
        "decision_journal_entries",
        ["user_id", "review_date"],
        unique=False,
    )

    op.create_table(
        "action_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=40), nullable=False),
        sa.Column("data_limitations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_action_plans_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_action_plans")),
    )
    op.create_index(op.f("ix_action_plans_user_id"), "action_plans", ["user_id"], unique=False)

    op.create_table(
        "agent_outputs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("intent", sa.String(length=120), nullable=True),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.String(length=40), nullable=False),
        sa.Column("data_limitations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("safety_status", sa.String(length=40), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_agent_outputs_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_outputs")),
    )
    op.create_index(op.f("ix_agent_outputs_user_id"), "agent_outputs", ["user_id"], unique=False)
    op.create_index("ix_agent_outputs_user_agent", "agent_outputs", ["user_id", "agent_name"], unique=False)

    op.create_table(
        "market_prices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("close_price", sa.Numeric(18, 6), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_market_prices_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_market_prices")),
        sa.UniqueConstraint("asset_id", "price_date", "source_name", name="uq_market_prices_asset_date_source"),
    )
    op.create_index("ix_market_prices_asset_date", "market_prices", ["asset_id", "price_date"], unique=False)

    op.create_table(
        "news_articles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("related_symbols", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_articles")),
    )
    op.create_index("ix_news_articles_published_at", "news_articles", ["published_at"], unique=False)

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_watchlist_items_asset_id_assets")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_watchlist_items_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_watchlist_items")),
        sa.UniqueConstraint("user_id", "asset_id", name="uq_watchlist_items_user_asset"),
    )
    op.create_index("ix_watchlist_items_user", "watchlist_items", ["user_id"], unique=False)

    op.create_table(
        "tax_lots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("holding_id", sa.String(length=36), nullable=False),
        sa.Column("acquired_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 8), nullable=False),
        sa.Column("cost_basis", sa.Numeric(18, 2), nullable=False),
        sa.Column("account_tax_type", sa.String(length=60), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["holding_id"], ["holdings.id"], name=op.f("fk_tax_lots_holding_id_holdings")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tax_lots")),
    )
    op.create_index("ix_tax_lots_holding_acquired", "tax_lots", ["holding_id", "acquired_date"], unique=False)

    op.create_table(
        "asset_scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("score_date", sa.Date(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("liquidity_score", sa.Integer(), nullable=False),
        sa.Column("diversification_score", sa.Integer(), nullable=False),
        sa.Column("income_yield_score", sa.Integer(), nullable=False),
        sa.Column("inflation_sensitivity_score", sa.Integer(), nullable=False),
        sa.Column("tax_complexity_score", sa.Integer(), nullable=False),
        sa.Column("methodology_version", sa.String(length=40), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_asset_scores_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_asset_scores")),
        sa.UniqueConstraint("asset_id", "score_date", name="uq_asset_scores_asset_date"),
    )
    op.create_index("ix_asset_scores_asset_date", "asset_scores", ["asset_id", "score_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_asset_scores_asset_date", table_name="asset_scores")
    op.drop_table("asset_scores")
    op.drop_index("ix_tax_lots_holding_acquired", table_name="tax_lots")
    op.drop_table("tax_lots")
    op.drop_index("ix_watchlist_items_user", table_name="watchlist_items")
    op.drop_table("watchlist_items")
    op.drop_index("ix_news_articles_published_at", table_name="news_articles")
    op.drop_table("news_articles")
    op.drop_index("ix_market_prices_asset_date", table_name="market_prices")
    op.drop_table("market_prices")
    op.drop_index("ix_agent_outputs_user_agent", table_name="agent_outputs")
    op.drop_index(op.f("ix_agent_outputs_user_id"), table_name="agent_outputs")
    op.drop_table("agent_outputs")
    op.drop_index(op.f("ix_action_plans_user_id"), table_name="action_plans")
    op.drop_table("action_plans")
    op.drop_index("ix_decision_journal_user_review_date", table_name="decision_journal_entries")
    op.drop_index(op.f("ix_decision_journal_entries_user_id"), table_name="decision_journal_entries")
    op.drop_table("decision_journal_entries")
    op.drop_index(op.f("ix_retirement_accounts_user_id"), table_name="retirement_accounts")
    op.drop_table("retirement_accounts")
    op.drop_index(op.f("ix_real_estate_properties_user_id"), table_name="real_estate_properties")
    op.drop_table("real_estate_properties")
    op.drop_index("ix_liabilities_user_type", table_name="liabilities")
    op.drop_index(op.f("ix_liabilities_user_id"), table_name="liabilities")
    op.drop_table("liabilities")
    op.drop_index("ix_holdings_portfolio_asset", table_name="holdings")
    op.drop_table("holdings")
    op.drop_index(op.f("ix_portfolios_user_id"), table_name="portfolios")
    op.drop_table("portfolios")
    op.drop_table("user_profiles")
    op.drop_index("ix_assets_asset_type_symbol", table_name="assets")
    op.drop_index(op.f("ix_assets_asset_type"), table_name="assets")
    op.drop_index(op.f("ix_assets_symbol"), table_name="assets")
    op.drop_table("assets")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

