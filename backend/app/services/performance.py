from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Mark
from app.schemas.performance import PerformanceResponse, PerformanceResultItem
from app.services.grades import calculate_grade
from app.services.students import get_student_or_404


def _round_metric(value: float) -> float:
    return round(float(value), 2)


def get_student_performance(db: Session, student_id: int) -> PerformanceResponse:
    get_student_or_404(db, student_id)

    marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student_id)
        .order_by(Mark.exam_id.asc(), Mark.id.asc())
    ).all()

    if not marks:
        return PerformanceResponse(
            student_id=student_id,
            total_marks=0,
            marks_obtained=0,
            percentage=0.0,
            average_marks=0.0,
            grade="F",
            total_subjects=0,
            results=[],
        )

    marks_obtained = float(sum(mark.marks for mark in marks))
    total_marks = len(marks) * 100
    percentage = _round_metric((marks_obtained / total_marks) * 100)
    average_marks = _round_metric(marks_obtained / len(marks))
    overall_grade = calculate_grade(average_marks)

    results = [
        PerformanceResultItem(
            mark_id=mark.id,
            exam_id=mark.exam_id,
            subject_id=mark.subject_id,
            marks=mark.marks,
            grade=calculate_grade(mark.marks),
        )
        for mark in marks
    ]

    return PerformanceResponse(
        student_id=student_id,
        total_marks=total_marks,
        marks_obtained=marks_obtained,
        percentage=percentage,
        average_marks=average_marks,
        grade=overall_grade,
        total_subjects=len(marks),
        results=results,
    )
