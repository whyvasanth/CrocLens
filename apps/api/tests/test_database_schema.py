from app.db.base import Base
from app import models  # noqa: F401


EXPECTED_TABLES = {
    "users",
    "user_profiles",
    "portfolios",
    "holdings",
    "assets",
    "liabilities",
    "real_estate_properties",
    "retirement_accounts",
    "decision_journal_entries",
    "action_plans",
    "agent_outputs",
    "market_prices",
    "news_articles",
    "watchlist_items",
    "tax_lots",
    "asset_scores",
}


def test_database_metadata_contains_phase_4_tables() -> None:
    assert set(Base.metadata.tables.keys()) == EXPECTED_TABLES


def test_core_foreign_keys_are_declared() -> None:
    holdings = Base.metadata.tables["holdings"]
    tax_lots = Base.metadata.tables["tax_lots"]
    market_prices = Base.metadata.tables["market_prices"]

    assert {fk.column.table.name for fk in holdings.foreign_keys} == {"assets", "portfolios"}
    assert {fk.column.table.name for fk in tax_lots.foreign_keys} == {"holdings"}
    assert {fk.column.table.name for fk in market_prices.foreign_keys} == {"assets"}

