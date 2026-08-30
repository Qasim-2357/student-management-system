from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.models import (
    Assignment,
    AssignmentSubmission,
    Attendance,
    Fee,
    Mark,
)
from app.schemas.academic_class import ClassResponse
from app.schemas.fee import FeeResponse
from app.schemas.student_report import (
    StudentReportAssignment,
    StudentReportAttendance,
    StudentReportAttendanceRecord,
    StudentReportAttendanceSummary,
    StudentReportFeesSummary,
    StudentReportMark,
    StudentReportMarksSummary,
    StudentReportResponse,
    StudentReportStudent,
    StudentReportSubmission,
)
from app.services.grading import calculate_grade
from app.services.students import get_student_or_404


def get_student_report(db: Session, student_id: int) -> StudentReportResponse:
    student = get_student_or_404(db, student_id)

    marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student_id)
        .options(selectinload(Mark.exam), selectinload(Mark.subject))
        .order_by(Mark.exam_id.asc(), Mark.subject_id.asc(), Mark.id.asc())
    ).all()
    attendance_records = db.scalars(
        select(Attendance)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.attendance_date.asc(), Attendance.id.asc())
    ).all()
    fees = db.scalars(
        select(Fee)
        .where(Fee.student_id == student_id)
        .order_by(Fee.due_date.asc(), Fee.id.asc())
    ).all()
    submissions = db.scalars(
        select(AssignmentSubmission)
        .where(AssignmentSubmission.student_id == student_id)
        .options(selectinload(AssignmentSubmission.assignment))
        .order_by(AssignmentSubmission.assignment_id.asc(), AssignmentSubmission.id.asc())
    ).all()

    submission_by_assignment = {
        submission.assignment_id: submission for submission in submissions
    }
    assignments = (
        db.scalars(
            select(Assignment)
            .where(Assignment.academic_class_id == student.academic_class_id)
            .order_by(Assignment.due_date.asc(), Assignment.id.asc())
        ).all()
        if student.academic_class_id is not None
        else []
    )

    present_records = sum(
        1 for record in attendance_records if record.status == "present"
    )
    absent_records = sum(
        1 for record in attendance_records if record.status == "absent"
    )
    total_attendance_records = len(attendance_records)
    attendance_percentage = (
        round((present_records / total_attendance_records) * 100, 2)
        if total_attendance_records
        else 0.0
    )

    total_marks_obtained = sum(float(mark.marks) for mark in marks)
    total_possible_marks = len(marks) * 100
    marks_percentage = (
        round((total_marks_obtained / total_possible_marks) * 100, 2)
        if total_possible_marks
        else 0.0
    )

    return StudentReportResponse(
        student=StudentReportStudent.model_validate(student),
        academic_class=(
            ClassResponse.model_validate(student.academic_class)
            if student.academic_class is not None
            else None
        ),
        marks=[
            StudentReportMark(
                mark_id=mark.id,
                exam_id=mark.exam_id,
                exam_name=mark.exam.name,
                exam_type=mark.exam.exam_type,
                exam_date=mark.exam.exam_date,
                subject_id=mark.subject_id,
                subject_name=mark.subject.name,
                subject_code=mark.subject.code,
                marks_obtained=mark.marks,
                grade=calculate_grade(mark.marks),
            )
            for mark in marks
        ],
        marks_summary=StudentReportMarksSummary(
            total_marks_obtained=total_marks_obtained,
            total_possible_marks=total_possible_marks,
            percentage=marks_percentage,
            overall_grade=calculate_grade(marks_percentage),
        ),
        attendance=StudentReportAttendance(
            summary=StudentReportAttendanceSummary(
                total_records=total_attendance_records,
                present_records=present_records,
                absent_records=absent_records,
                attendance_percentage=attendance_percentage,
            ),
            records=[
                StudentReportAttendanceRecord.model_validate(record)
                for record in attendance_records
            ],
        ),
        assignments=[
            StudentReportAssignment(
                id=assignment.id,
                title=assignment.title,
                description=assignment.description,
                subject_id=assignment.subject_id,
                academic_class_id=assignment.academic_class_id,
                due_date=assignment.due_date,
                submission=(
                    StudentReportSubmission.model_validate(
                        submission_by_assignment[assignment.id]
                    )
                    if assignment.id in submission_by_assignment
                    else None
                ),
            )
            for assignment in assignments
        ],
        fees=StudentReportFeesSummary(
            total_amount=round(sum(float(fee.amount) for fee in fees), 2),
            total_paid_amount=round(sum(float(fee.paid_amount) for fee in fees), 2),
            total_due_amount=round(sum(fee.due_amount for fee in fees), 2),
            records=[FeeResponse.model_validate(fee) for fee in fees],
        ),
    )
