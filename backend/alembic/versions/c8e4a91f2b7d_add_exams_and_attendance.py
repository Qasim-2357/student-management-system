"""add exams and attendance

Revision ID: c8e4a91f2b7d
Revises: 042056e7b6c4
Create Date: 2026-08-29 13:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8e4a91f2b7d"
down_revision: Union[str, Sequence[str], None] = "042056e7b6c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "exams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=False),
        sa.Column("academic_class_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["academic_class_id"],
            ["academic_classes.id"],
            name="fk_exams_academic_class_id_academic_classes",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exams_exam_date"), "exams", ["exam_date"], unique=False)
    op.create_index(
        op.f("ix_exams_academic_class_id"),
        "exams",
        ["academic_class_id"],
        unique=False,
    )

    op.create_table(
        "attendances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint(
            "status IN ('present', 'absent')",
            name="ck_attendances_status",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            name="fk_attendances_student_id_students",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            "attendance_date",
            name="uq_attendances_student_date",
        ),
    )
    op.create_index(
        op.f("ix_attendances_student_id"),
        "attendances",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attendances_attendance_date"),
        "attendances",
        ["attendance_date"],
        unique=False,
    )

    op.add_column("marks", sa.Column("exam_id", sa.Integer(), nullable=False))
    op.create_index(op.f("ix_marks_exam_id"), "marks", ["exam_id"], unique=False)
    op.create_index(op.f("ix_marks_student_id"), "marks", ["student_id"], unique=False)
    op.create_index(op.f("ix_marks_subject_id"), "marks", ["subject_id"], unique=False)
    op.create_foreign_key(
        "fk_marks_exam_id_exams",
        "marks",
        "exams",
        ["exam_id"],
        ["id"],
    )

   

    op.alter_column("marks", "exam_id", existing_type=sa.Integer(), nullable=False)
    op.create_unique_constraint(
        "uq_marks_exam_student_subject",
        "marks",
        ["exam_id", "student_id", "subject_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_marks_exam_student_subject", "marks", type_="unique")
    op.drop_constraint("fk_marks_exam_id_exams", "marks", type_="foreignkey")
    op.drop_index(op.f("ix_marks_subject_id"), table_name="marks")
    op.drop_index(op.f("ix_marks_student_id"), table_name="marks")
    op.drop_index(op.f("ix_marks_exam_id"), table_name="marks")
    op.drop_column("marks", "exam_id")

    op.drop_index(op.f("ix_attendances_attendance_date"), table_name="attendances")
    op.drop_index(op.f("ix_attendances_student_id"), table_name="attendances")
    op.drop_table("attendances")

    op.drop_index(op.f("ix_exams_academic_class_id"), table_name="exams")
    op.drop_index(op.f("ix_exams_exam_date"), table_name="exams")
    op.drop_table("exams")

   
