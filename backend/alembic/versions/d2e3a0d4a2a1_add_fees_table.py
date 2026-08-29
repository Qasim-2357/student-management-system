"""add fees table

Revision ID: d2e3a0d4a2a1
Revises: c8e4a91f2b7d
Create Date: 2026-08-29 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2e3a0d4a2a1"
down_revision: Union[str, Sequence[str], None] = "c8e4a91f2b7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("paid_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("amount >= 0", name="ck_fees_amount_non_negative"),
        sa.CheckConstraint("paid_amount >= 0", name="ck_fees_paid_amount_non_negative"),
        sa.CheckConstraint("paid_amount <= amount", name="ck_fees_paid_amount_lte_amount"),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            name="fk_fees_student_id_students",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fees_student_id"), "fees", ["student_id"], unique=False)
    op.create_index(op.f("ix_fees_due_date"), "fees", ["due_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fees_due_date"), table_name="fees")
    op.drop_index(op.f("ix_fees_student_id"), table_name="fees")
    op.drop_table("fees")
