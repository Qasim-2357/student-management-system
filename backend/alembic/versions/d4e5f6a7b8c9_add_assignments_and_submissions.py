"""add assignments and submissions

Revision ID: d4e5f6a7b8c9
Revises: d2e3a0d4a2a1
Create Date: 2026-08-29 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "d2e3a0d4a2a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("academic_class_id", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name="fk_assignments_subject_id_subjects",
        ),
        sa.ForeignKeyConstraint(
            ["academic_class_id"],
            ["academic_classes.id"],
            name="fk_assignments_academic_class_id_academic_classes",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_assignments_subject_id"),
        "assignments",
        ["subject_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assignments_academic_class_id"),
        "assignments",
        ["academic_class_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assignments_due_date"),
        "assignments",
        ["due_date"],
        unique=False,
    )

    op.create_table(
        "assignment_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assignment_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'submitted', 'late')",
            name="ck_assignment_submissions_status",
        ),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["assignments.id"],
            name="fk_assignment_submissions_assignment_id_assignments",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            name="fk_assignment_submissions_student_id_students",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "assignment_id",
            "student_id",
            name="uq_assignment_submissions_assignment_student",
        ),
    )
    op.create_index(
        op.f("ix_assignment_submissions_assignment_id"),
        "assignment_submissions",
        ["assignment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assignment_submissions_student_id"),
        "assignment_submissions",
        ["student_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_assignment_submissions_student_id"),
        table_name="assignment_submissions",
    )
    op.drop_index(
        op.f("ix_assignment_submissions_assignment_id"),
        table_name="assignment_submissions",
    )
    op.drop_constraint(
        "uq_assignment_submissions_assignment_student",
        "assignment_submissions",
        type_="unique",
    )
    op.drop_table("assignment_submissions")

    op.drop_index(op.f("ix_assignments_due_date"), table_name="assignments")
    op.drop_index(
        op.f("ix_assignments_academic_class_id"),
        table_name="assignments",
    )
    op.drop_index(op.f("ix_assignments_subject_id"), table_name="assignments")
    op.drop_table("assignments")
