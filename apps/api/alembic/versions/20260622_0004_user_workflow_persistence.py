"""add user workflow persistence fields

Revision ID: 20260622_0004
Revises: 20260622_0003
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa

try:
    from sqlalchemy.dialects import postgresql
except ImportError:  # pragma: no cover
    postgresql = None


revision = "20260622_0004"
down_revision = "20260622_0003"
branch_labels = None
depends_on = None


def _json_type() -> sa.types.TypeEngine:
    if postgresql is not None:
        return postgresql.JSONB(astext_type=sa.Text())
    return sa.JSON()


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("store_assistant_history", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("user_profiles", sa.Column("allow_product_analytics", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("user_profiles", sa.Column("allow_external_integrations", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("user_profiles", sa.Column("data_retention_days", sa.Integer(), server_default="30", nullable=False))

    op.add_column("decision_journal_entries", sa.Column("asset_symbol", sa.String(length=40), nullable=True))
    op.add_column("decision_journal_entries", sa.Column("status", sa.String(length=40), server_default="open", nullable=False))
    op.add_column("decision_journal_entries", sa.Column("actual_outcome", sa.Text(), nullable=True))
    op.add_column("decision_journal_entries", sa.Column("reflection", sa.Text(), nullable=True))

    op.add_column("action_plans", sa.Column("evidence", _json_type(), server_default=sa.text("'[]'"), nullable=False))
    op.add_column("action_plans", sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("action_plans", sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("action_plans", "dismissed_at")
    op.drop_column("action_plans", "completed_at")
    op.drop_column("action_plans", "evidence")

    op.drop_column("decision_journal_entries", "reflection")
    op.drop_column("decision_journal_entries", "actual_outcome")
    op.drop_column("decision_journal_entries", "status")
    op.drop_column("decision_journal_entries", "asset_symbol")

    op.drop_column("user_profiles", "data_retention_days")
    op.drop_column("user_profiles", "allow_external_integrations")
    op.drop_column("user_profiles", "allow_product_analytics")
    op.drop_column("user_profiles", "store_assistant_history")
