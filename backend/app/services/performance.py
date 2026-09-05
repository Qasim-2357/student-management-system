from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import Student, Mark
from app.schemas.performance import PerformanceResponse, PerformanceResultItem
from app.services.grading import calculate_grade


def get_student_performance(db: Session, student_id: int) -> PerformanceResponse:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )

    marks: List[Mark] = (
        db.query(Mark)
        .filter(Mark.student_id == student_id)
        .order_by(Mark.exam_id.asc(), Mark.id.asc())
        .all()
    )

    total_marks = len(marks) * 100
    marks_obtained = float(sum(m.marks for m in marks)) if marks else 0.0
    percentage = round((marks_obtained / total_marks) * 100.0, 2) if total_marks > 0 else 0.0
    average_marks = round(marks_obtained / len(marks), 2) if marks else 0.0
    grade = calculate_grade(percentage) if marks else "F"
    total_subjects = len({m.subject_id for m in marks})

    results_list: List[PerformanceResultItem] = [
        PerformanceResultItem(
            mark_id=m.id,
            exam_id=m.exam_id,
            subject_id=m.subject_id,
            marks=float(m.marks),
            grade=calculate_grade(m.marks),
        )
        for m in marks
    ]

    return PerformanceResponse(
        student_id=student.id,
        total_marks=total_marks,
        marks_obtained=marks_obtained,
        percentage=percentage,
        average_marks=average_marks,
        grade=grade,
        total_subjects=total_subjects,
        results=results_list,
    )


get_student_performance_summary = get_student_performance
get_performance_summary = get_student_performance