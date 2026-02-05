"""Initial migration - create risks table

Revision ID: 4858716f5228
Revises:
Create Date: 2026-02-05 09:54:15.144121

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4858716f5228"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create risks table with all fields.

    This migration creates the main risks table for risk assessment tracking.
    Includes fields for risk details, scoring, status tracking, and audit timestamps.
    """
    op.create_table(
        "risks",
        # Primary Key
        sa.Column("id", sa.UUID(), nullable=False),
        # Business Identifier
        sa.Column("risk_number", sa.String(length=20), nullable=False),
        # Core Risk Information
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        # Risk Classification
        sa.Column(
            "severity",
            sa.Enum("critical", "high", "medium", "low", name="riskseverity"),
            nullable=False,
        ),
        sa.Column(
            "likelihood",
            sa.Enum("high", "medium", "low", name="risklikelihood"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum("technical", "operational", "compliance", name="riskcategory"),
            nullable=False,
        ),
        # Risk Scoring
        sa.Column("impact_score", sa.Float(), nullable=False),
        # Status Tracking
        sa.Column(
            "status",
            sa.Enum("open", "in_progress", "mitigated", "accepted", name="riskstatus"),
            nullable=False,
        ),
        # Assignment & Mitigation
        sa.Column("assigned_to", sa.String(length=255), nullable=False),
        sa.Column("mitigation_plan", sa.Text(), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        # Audit Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("risk_number"),
    )

    # Create indexes for frequently queried fields
    op.create_index(op.f("ix_risks_severity"), "risks", ["severity"], unique=False)
    op.create_index(op.f("ix_risks_status"), "risks", ["status"], unique=False)
    op.create_index(op.f("ix_risks_assigned_to"), "risks", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_risks_created_at"), "risks", ["created_at"], unique=False)


def downgrade() -> None:
    """
    Drop risks table and related indexes.

    Rollback migration by removing the risks table and all associated
    database objects (indexes, enums).
    """
    # Drop indexes first
    op.drop_index(op.f("ix_risks_created_at"), table_name="risks")
    op.drop_index(op.f("ix_risks_assigned_to"), table_name="risks")
    op.drop_index(op.f("ix_risks_status"), table_name="risks")
    op.drop_index(op.f("ix_risks_severity"), table_name="risks")

    # Drop table
    op.drop_table("risks")

    # Drop enums (PostgreSQL-specific only)
    # SQLite doesn't support CREATE TYPE/DROP TYPE, so skip for SQLite
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS riskstatus")
        op.execute("DROP TYPE IF EXISTS riskcategory")
        op.execute("DROP TYPE IF EXISTS risklikelihood")
        op.execute("DROP TYPE IF EXISTS riskseverity")
