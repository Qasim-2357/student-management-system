from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Attendance
from app.schemas.attendance_report import (
    AttendanceReportRecord,
    AttendanceReportResponse,
    AttendanceReportStudent,
    AttendanceReportSummary,
)
from app.services.students import get_student_or_404


def get_student_attendance_report(
    db: Session,
    student_id: int,
) -> AttendanceReportResponse:
    student = get_student_or_404(db, student_id)
    records = db.scalars(
        select(Attendance)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.attendance_date.asc(), Attendance.id.asc())
    ).all()

    present_records = sum(1 for record in records if record.status == "present")
    absent_records = sum(1 for record in records if record.status == "absent")
    total_records = len(records)
    attendance_percentage = (
        round((present_records / total_records) * 100, 2)
        if total_records
        else 0.0
    )

    return AttendanceReportResponse(
        student=AttendanceReportStudent.model_validate(student),
        summary=AttendanceReportSummary(
            total_records=total_records,
            present_records=present_records,
            absent_records=absent_records,
            attendance_percentage=attendance_percentage,
        ),
        attendance_records=[
            AttendanceReportRecord.model_validate(record) for record in records
        ],
    )
