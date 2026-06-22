"""add market observation cache tables

Revision ID: 20260622_0003
Revises: 20260622_0002
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260622_0003"
down_revision: Union[str, None] = "20260622_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.add_column(
        "market_prices",
        sa.Column("currency", sa.String(length=8), server_default="USD", nullable=False),
    )
    op.add_column("market_prices", sa.Column("data_as_of", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "market_prices",
        sa.Column("provider_status", sa.String(length=40), server_default="healthy", nullable=False),
    )
    op.add_column(
        "market_prices",
        sa.Column("data_quality", sa.String(length=40), server_default="unknown", nullable=False),
    )
    op.add_column(
        "market_prices",
        sa.Column("is_stale", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "market_prices",
        sa.Column("is_sample_data", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("market_prices", sa.Column("source_url", sa.String(length=500), nullable=True))
    op.add_column(
        "market_prices",
        sa.Column("data_limitations", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
    )
    op.add_column(
        "market_prices",
        sa.Column("raw_response_metadata", JSON_TYPE, server_default=sa.text("'{}'"), nullable=False),
    )
    op.create_index(
        "ix_market_prices_asset_provider_retrieved",
        "market_prices",
        ["asset_id", "source_name", "retrieved_at"],
        unique=False,
    )

    op.create_table(
        "provider_ingestion_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider_name", sa.String(length=120), nullable=False),
        sa.Column("operation", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_requested", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_accepted", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_rejected", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", JSON_TYPE, server_default=sa.text("'{}'"), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provider_ingestion_runs")),
    )
    op.create_index(
        "ix_provider_ingestion_runs_provider_started",
        "provider_ingestion_runs",
        ["provider_name", "started_at"],
        unique=False,
    )
    op.create_index(
        "ix_provider_ingestion_runs_status",
        "provider_ingestion_runs",
        ["status"],
        unique=False,
    )

    op.create_table(
        "provider_errors",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider_name", sa.String(length=120), nullable=False),
        sa.Column("operation", sa.String(length=120), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=True),
        sa.Column("symbol_or_series", sa.String(length=80), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("retryable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], name=op.f("fk_provider_errors_asset_id_assets")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provider_errors")),
    )
    op.create_index(
        "ix_provider_errors_provider_created",
        "provider_errors",
        ["provider_name", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_provider_errors_asset_provider",
        "provider_errors",
        ["asset_id", "provider_name"],
        unique=False,
    )

    op.create_table(
        "portfolio_net_worth_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("portfolio_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("total_assets", sa.Numeric(18, 2), nullable=False),
        sa.Column("total_liabilities", sa.Numeric(18, 2), nullable=False),
        sa.Column("net_worth", sa.Numeric(18, 2), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("data_quality", sa.String(length=40), server_default="manual", nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], name=op.f("fk_portfolio_net_worth_snapshots_portfolio_id_portfolios")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_portfolio_net_worth_snapshots_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_portfolio_net_worth_snapshots")),
        sa.UniqueConstraint("portfolio_id", "snapshot_date", name="uq_portfolio_snapshots_portfolio_date"),
    )
    op.create_index(
        "ix_portfolio_snapshots_portfolio_date",
        "portfolio_net_worth_snapshots",
        ["portfolio_id", "snapshot_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_portfolio_snapshots_portfolio_date", table_name="portfolio_net_worth_snapshots")
    op.drop_table("portfolio_net_worth_snapshots")
    op.drop_index("ix_provider_errors_asset_provider", table_name="provider_errors")
    op.drop_index("ix_provider_errors_provider_created", table_name="provider_errors")
    op.drop_table("provider_errors")
    op.drop_index("ix_provider_ingestion_runs_status", table_name="provider_ingestion_runs")
    op.drop_index("ix_provider_ingestion_runs_provider_started", table_name="provider_ingestion_runs")
    op.drop_table("provider_ingestion_runs")
    op.drop_index("ix_market_prices_asset_provider_retrieved", table_name="market_prices")
    op.drop_column("market_prices", "raw_response_metadata")
    op.drop_column("market_prices", "data_limitations")
    op.drop_column("market_prices", "source_url")
    op.drop_column("market_prices", "is_sample_data")
    op.drop_column("market_prices", "is_stale")
    op.drop_column("market_prices", "data_quality")
    op.drop_column("market_prices", "provider_status")
    op.drop_column("market_prices", "data_as_of")
    op.drop_column("market_prices", "currency")
