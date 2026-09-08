"""align mark foreign key cascades

Revision ID: 5ac033fc3ac3
Revises: d4e5f6a7b8c9
Create Date: 2026-09-07 17:29:36.519149

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5ac033fc3ac3"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "marks_student_id_fkey",
        "marks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "marks_subject_id_fkey",
        "marks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_marks_exam_id_exams",
        "marks",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "fk_marks_student_id_students",
        "marks",
        "students",
        ["student_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_marks_subject_id_subjects",
        "marks",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_marks_exam_id_exams",
        "marks",
        "exams",
        ["exam_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_marks_student_id_students",
        "marks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_marks_subject_id_subjects",
        "marks",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_marks_exam_id_exams",
        "marks",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "marks_student_id_fkey",
        "marks",
        "students",
        ["student_id"],
        ["id"],
    )
    op.create_foreign_key(
        "marks_subject_id_fkey",
        "marks",
        "subjects",
        ["subject_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_marks_exam_id_exams",
        "marks",
        "exams",
        ["exam_id"],
        ["id"],
    )