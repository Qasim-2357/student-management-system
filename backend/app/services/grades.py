from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Mark
from app.schemas.grade import MarkGradeResponse, StudentGradeItem, StudentGradesResponse
from app.services.marks import get_mark_or_404
from app.services.students import get_student_or_404

GRADE_THRESHOLDS = (
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0, "F"),
)


def calculate_grade(marks: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if marks >= threshold:
            return grade
    return "F"


def get_mark_grade(db: Session, mark_id: int) -> MarkGradeResponse:
    mark = get_mark_or_404(db, mark_id)
    return MarkGradeResponse(
        mark_id=mark.id,
        student_id=mark.student_id,
        subject_id=mark.subject_id,
        exam_id=mark.exam_id,
        marks=mark.marks,
        grade=calculate_grade(mark.marks),
    )


def get_student_grades(db: Session, student_id: int) -> StudentGradesResponse:
    get_student_or_404(db, student_id)

    marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student_id)
        .order_by(Mark.exam_id.asc(), Mark.id.asc())
    ).all()

    return StudentGradesResponse(
        student_id=student_id,
        grades=[
            StudentGradeItem(
                mark_id=mark.id,
                exam_id=mark.exam_id,
                subject_id=mark.subject_id,
                marks=mark.marks,
                grade=calculate_grade(mark.marks),
            )
            for mark in marks
        ],
    )