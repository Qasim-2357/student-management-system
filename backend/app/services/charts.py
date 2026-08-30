from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Attendance, Mark
from app.schemas.charts import (
    AttendanceChartResponse,
    ExamChartItem,
    ExamChartResponse,
    MarksChartItem,
    MarksChartResponse,
)
from app.services.students import get_student_or_404


def _round_metric(value: float) -> float:
    return round(float(value), 2)


def get_student_marks_chart(db: Session, student_id: int) -> MarksChartResponse:
    get_student_or_404(db, student_id)

    marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student_id)
        .options(selectinload(Mark.subject))
        .order_by(Mark.subject_id.asc(), Mark.id.asc())
    ).all()

    if not marks:
        return MarksChartResponse(student_id=student_id, data=[])

    grouped: dict[int, dict[str, float | int | str]] = {}
    for mark in marks:
        entry = grouped.setdefault(
            mark.subject_id,
            {"subject_name": mark.subject.name, "total": 0.0, "count": 0},
        )
        entry["total"] = float(entry["total"]) + float(mark.marks)
        entry["count"] = int(entry["count"]) + 1

    data = [
        MarksChartItem(
            subject_id=subject_id,
            subject_name=str(grouped[subject_id]["subject_name"]),
            average_marks=_round_metric(
                float(grouped[subject_id]["total"]) / int(grouped[subject_id]["count"])
            ),
        )
        for subject_id in sorted(grouped)
    ]

    return MarksChartResponse(student_id=student_id, data=data)


def get_student_exam_chart(db: Session, student_id: int) -> ExamChartResponse:
    get_student_or_404(db, student_id)

    marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student_id)
        .options(selectinload(Mark.exam))
        .order_by(Mark.exam_id.asc(), Mark.id.asc())
    ).all()

    if not marks:
        return ExamChartResponse(student_id=student_id, data=[])

    grouped: dict[int, dict[str, float | int | str]] = {}
    for mark in marks:
        entry = grouped.setdefault(
            mark.exam_id,
            {"exam_name": mark.exam.name, "total": 0.0, "count": 0},
        )
        entry["total"] = float(entry["total"]) + float(mark.marks)
        entry["count"] = int(entry["count"]) + 1

    data = [
        ExamChartItem(
            exam_id=exam_id,
            exam_name=str(grouped[exam_id]["exam_name"]),
            average_marks=_round_metric(
                float(grouped[exam_id]["total"]) / int(grouped[exam_id]["count"])
            ),
        )
        for exam_id in sorted(grouped)
    ]

    return ExamChartResponse(student_id=student_id, data=data)


def get_student_attendance_chart(
    db: Session,
    student_id: int,
) -> AttendanceChartResponse:
    get_student_or_404(db, student_id)

    records = db.scalars(
        select(Attendance).where(Attendance.student_id == student_id)
    ).all()

    present = sum(1 for record in records if record.status == "present")
    absent = sum(1 for record in records if record.status == "absent")
    total = len(records)
    percentage = _round_metric((present / total) * 100) if total else 0.0

    return AttendanceChartResponse(
        student_id=student_id,
        present=present,
        absent=absent,
        total=total,
        percentage=percentage,
    )
