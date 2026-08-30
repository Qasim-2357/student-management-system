from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.models import (
    AcademicClass,
    Assignment,
    AssignmentSubmission,
    Attendance,
    Exam,
    Fee,
    Student,
    Subject,
    Teacher,
)
from app.schemas.dashboard import (
    AdminDashboardResponse,
    RecentStudentItem,
    UpcomingExamItem,
)


def _safe_percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((float(numerator) / float(denominator)) * 100, 2)


def get_admin_dashboard(db: Session) -> AdminDashboardResponse:
    total_students = db.scalar(select(func.count()).select_from(Student)) or 0
    total_teachers = db.scalar(select(func.count()).select_from(Teacher)) or 0
    total_classes = db.scalar(select(func.count()).select_from(AcademicClass)) or 0
    total_subjects = db.scalar(select(func.count()).select_from(Subject)) or 0
    total_exams = db.scalar(select(func.count()).select_from(Exam)) or 0
    total_assignments = db.scalar(select(func.count()).select_from(Assignment)) or 0
    total_submissions = db.scalar(
        select(func.count()).select_from(AssignmentSubmission)
    ) or 0

    total_fee_records = db.scalar(select(func.count()).select_from(Fee)) or 0
    paid_fee_records = db.scalar(
        select(func.count()).select_from(Fee).where(Fee.paid_amount >= Fee.amount)
    ) or 0
    pending_fee_records = total_fee_records - paid_fee_records

    total_attendance_records = db.scalar(
        select(func.count()).select_from(Attendance)
    ) or 0
    present_attendance_records = db.scalar(
        select(func.count()).select_from(Attendance).where(Attendance.status == "present")
    ) or 0
    overall_attendance_percentage = _safe_percentage(
        present_attendance_records,
        total_attendance_records,
    )

    recent_students = db.scalars(
        select(Student)
        .order_by(Student.created_at.desc(), Student.id.desc())
        .limit(5)
    ).all()
    recent_student_items = [
        RecentStudentItem(
            id=student.id,
            name=student.name,
            email=student.email,
            created_at=student.created_at,
        )
        for student in recent_students
    ]

    upcoming_exams = db.scalars(
        select(Exam)
        .options(selectinload(Exam.academic_class))
        .where(Exam.exam_date >= date.today())
        .order_by(Exam.exam_date.asc(), Exam.id.asc())
        .limit(5)
    ).all()
    upcoming_exam_items = [
        UpcomingExamItem(
            id=exam.id,
            name=exam.name,
            exam_date=exam.exam_date,
            academic_class_name=exam.academic_class.name if exam.academic_class else None,
        )
        for exam in upcoming_exams
    ]

    return AdminDashboardResponse(
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_exams=total_exams,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        total_fee_records=total_fee_records,
        paid_fee_records=paid_fee_records,
        pending_fee_records=pending_fee_records,
        total_attendance_records=total_attendance_records,
        overall_attendance_percentage=overall_attendance_percentage,
        recent_students=recent_student_items,
        upcoming_exams=upcoming_exam_items,
    )
