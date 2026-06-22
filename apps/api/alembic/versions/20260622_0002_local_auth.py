"""add local authentication fields

Revision ID: 20260622_0002
Revises: 20260505_0001
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260622_0002"
down_revision: Union[str, None] = "20260505_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(length=40), server_default="local", nullable=False),
    )
    op.add_column("users", sa.Column("external_auth_subject", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_users_external_auth_subject"), "users", ["external_auth_subject"], unique=True)

    op.create_table(
        "local_auth_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_local_auth_sessions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_local_auth_sessions")),
        sa.UniqueConstraint("token_hash", name="uq_local_auth_sessions_token_hash"),
    )
    op.create_index(op.f("ix_local_auth_sessions_user_id"), "local_auth_sessions", ["user_id"], unique=False)
    op.create_index(
        "ix_local_auth_sessions_user_expires",
        "local_auth_sessions",
        ["user_id", "expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_local_auth_sessions_user_expires", table_name="local_auth_sessions")
    op.drop_index(op.f("ix_local_auth_sessions_user_id"), table_name="local_auth_sessions")
    op.drop_table("local_auth_sessions")
    op.drop_index(op.f("ix_users_external_auth_subject"), table_name="users")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "external_auth_subject")
    op.drop_column("users", "auth_provider")
