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
    Mark,
    Student,
    Subject,
    Teacher,
)
from app.schemas.academic_class import ClassResponse
from app.schemas.dashboard import (
    AdminDashboardResponse,
    AssignedClassItem,
    AssignedSubjectItem,
    DashboardOverviewResponse,
    RecentStudentItem,
    StudentDashboardResponse,
    StudentDashboardOverviewResponse,
    StudentInfo,
    StudentMarkItem,
    StudentCourseCount,
    TeacherDashboardResponse,
    TeacherInfo,
    UpcomingExamItem,
)
from app.services.grades import calculate_grade
from app.services.performance import get_student_performance


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


def get_dashboard_overview(db: Session) -> DashboardOverviewResponse:
    total_students = db.scalar(select(func.count()).select_from(Student)) or 0
    students_by_course = db.execute(
        select(Student.course, func.count(Student.id))
        .group_by(Student.course)
        .order_by(Student.course.asc())
    ).all()

    total_teachers = db.scalar(select(func.count()).select_from(Teacher)) or 0
    total_classes = db.scalar(select(func.count()).select_from(AcademicClass)) or 0
    total_subjects = db.scalar(select(func.count()).select_from(Subject)) or 0
    total_exams = db.scalar(select(func.count()).select_from(Exam)) or 0
    total_marks_records = db.scalar(select(func.count()).select_from(Mark)) or 0

    total_attendance_records = (
        db.scalar(select(func.count()).select_from(Attendance)) or 0
    )
    present_count = db.scalar(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.status == "present")
    ) or 0
    absent_count = db.scalar(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.status == "absent")
    ) or 0

    total_assignments = db.scalar(select(func.count()).select_from(Assignment)) or 0
    total_submissions = (
        db.scalar(select(func.count()).select_from(AssignmentSubmission)) or 0
    )

    total_fee_records = db.scalar(select(func.count()).select_from(Fee)) or 0
    total_fee_amount = db.scalar(select(func.sum(Fee.amount))) or 0.0
    total_paid_amount = db.scalar(select(func.sum(Fee.paid_amount))) or 0.0
    total_due_amount = db.scalar(
        select(func.sum(Fee.amount - Fee.paid_amount))
    ) or 0.0

    return DashboardOverviewResponse(
        total_students=total_students,
        students_by_course=[
            StudentCourseCount(course=course, count=count)
            for course, count in students_by_course
        ],
        total_teachers=total_teachers,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_exams=total_exams,
        total_marks_records=total_marks_records,
        total_attendance_records=total_attendance_records,
        present_count=present_count,
        absent_count=absent_count,
        attendance_percentage=_safe_percentage(
            present_count,
            total_attendance_records,
        ),
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        total_fee_records=total_fee_records,
        total_fee_amount=round(float(total_fee_amount), 2),
        total_paid_amount=round(float(total_paid_amount), 2),
        total_due_amount=round(float(total_due_amount), 2),
    )


def get_teacher_dashboard(db: Session, teacher: Teacher) -> TeacherDashboardResponse:
    """Build a database-driven dashboard for the given teacher.

    Only statistics that can be accurately derived from the existing schema
    are included. In particular:

    - ``Mark`` does not record which teacher entered a mark, so per-teacher
      "marks entered" statistics are not calculated.
    - ``Attendance`` does not record a teacher or an academic class directly.
      It is only linked to a ``Student``, and a ``Student`` is linked to an
      ``AcademicClass``. Attendance statistics below are therefore derived
      through that existing Student -> AcademicClass relationship, limited to
      students who belong to one of the teacher's assigned classes.
    - ``Assignment`` records both a ``subject_id`` and an
      ``academic_class_id``. Since a ``Teacher`` is independently linked to a
      set of subjects and a set of classes (there is no single table linking
      a specific subject to a specific class for a specific teacher), an
      assignment is only counted as "relevant" to the teacher when both its
      subject and its academic class are among the teacher's assigned
      subjects and classes. This avoids assuming a teacher is responsible for
      a subject in a class that was never assigned to them.
    """

    # Reload the teacher with its many-to-many relationships eagerly loaded
    # so the collections below don't trigger extra lazy-load queries.
    teacher = db.scalars(
        select(Teacher)
        .where(Teacher.id == teacher.id)
        .options(
            selectinload(Teacher.academic_classes),
            selectinload(Teacher.subjects),
        )
    ).one()

    class_ids = [academic_class.id for academic_class in teacher.academic_classes]
    subject_ids = [subject.id for subject in teacher.subjects]

    total_assigned_classes = len(class_ids)
    total_assigned_subjects = len(subject_ids)

    total_students = 0
    if class_ids:
        total_students = db.scalar(
            select(func.count(func.distinct(Student.id))).where(
                Student.academic_class_id.in_(class_ids)
            )
        ) or 0

    total_relevant_exams = 0
    upcoming_exam_items: list[UpcomingExamItem] = []
    if class_ids:
        total_relevant_exams = db.scalar(
            select(func.count())
            .select_from(Exam)
            .where(Exam.academic_class_id.in_(class_ids))
        ) or 0

        upcoming_exams = db.scalars(
            select(Exam)
            .options(selectinload(Exam.academic_class))
            .where(
                Exam.academic_class_id.in_(class_ids),
                Exam.exam_date >= date.today(),
            )
            .order_by(Exam.exam_date.asc(), Exam.id.asc())
            .limit(5)
        ).all()
        upcoming_exam_items = [
            UpcomingExamItem(
                id=exam.id,
                name=exam.name,
                exam_date=exam.exam_date,
                academic_class_name=(
                    exam.academic_class.name if exam.academic_class else None
                ),
            )
            for exam in upcoming_exams
        ]

    total_assignments = 0
    total_submissions = 0
    submitted_submissions = 0
    pending_submissions = 0
    if class_ids and subject_ids:
        relevant_assignment_ids = select(Assignment.id).where(
            Assignment.academic_class_id.in_(class_ids),
            Assignment.subject_id.in_(subject_ids),
        )

        total_assignments = db.scalar(
            select(func.count())
            .select_from(Assignment)
            .where(
                Assignment.academic_class_id.in_(class_ids),
                Assignment.subject_id.in_(subject_ids),
            )
        ) or 0

        total_submissions = db.scalar(
            select(func.count())
            .select_from(AssignmentSubmission)
            .where(AssignmentSubmission.assignment_id.in_(relevant_assignment_ids))
        ) or 0

        submitted_submissions = db.scalar(
            select(func.count())
            .select_from(AssignmentSubmission)
            .where(
                AssignmentSubmission.assignment_id.in_(relevant_assignment_ids),
                AssignmentSubmission.status.in_(["submitted", "late"]),
            )
        ) or 0

        pending_submissions = db.scalar(
            select(func.count())
            .select_from(AssignmentSubmission)
            .where(
                AssignmentSubmission.assignment_id.in_(relevant_assignment_ids),
                AssignmentSubmission.status == "pending",
            )
        ) or 0

    total_attendance_records = 0
    present_attendance_records = 0
    overall_attendance_percentage = 0.0
    if class_ids:
        relevant_student_ids = select(Student.id).where(
            Student.academic_class_id.in_(class_ids)
        )

        total_attendance_records = db.scalar(
            select(func.count())
            .select_from(Attendance)
            .where(Attendance.student_id.in_(relevant_student_ids))
        ) or 0

        present_attendance_records = db.scalar(
            select(func.count())
            .select_from(Attendance)
            .where(
                Attendance.student_id.in_(relevant_student_ids),
                Attendance.status == "present",
            )
        ) or 0

        overall_attendance_percentage = _safe_percentage(
            present_attendance_records,
            total_attendance_records,
        )

    student_counts_by_class = {}
    if class_ids:
        student_counts_by_class = dict(
            db.execute(
                select(Student.academic_class_id, func.count(Student.id))
                .where(Student.academic_class_id.in_(class_ids))
                .group_by(Student.academic_class_id)
            ).all()
        )

    assigned_class_items = []
    for academic_class in teacher.academic_classes:
        assigned_class_items.append(
            AssignedClassItem(
                id=academic_class.id,
                name=academic_class.name,
                code=academic_class.code,
                student_count=student_counts_by_class.get(academic_class.id, 0),
            )
        )
    assigned_class_items.sort(key=lambda item: item.id)

    assigned_subject_items = sorted(
        (
            AssignedSubjectItem(id=subject.id, name=subject.name, code=subject.code)
            for subject in teacher.subjects
        ),
        key=lambda item: item.id,
    )

    return TeacherDashboardResponse(
        teacher=TeacherInfo.model_validate(teacher),
        total_assigned_classes=total_assigned_classes,
        total_assigned_subjects=total_assigned_subjects,
        total_students=total_students,
        total_relevant_exams=total_relevant_exams,
        upcoming_exams=upcoming_exam_items,
        total_assignments=total_assignments,
        total_submissions=total_submissions,
        submitted_submissions=submitted_submissions,
        pending_submissions=pending_submissions,
        total_attendance_records=total_attendance_records,
        present_attendance_records=present_attendance_records,
        overall_attendance_percentage=overall_attendance_percentage,
        assigned_classes=assigned_class_items,
        assigned_subjects=assigned_subject_items,
    )


def get_student_dashboard(db: Session, student: Student) -> StudentDashboardResponse:
    """Build a database-driven dashboard for the given student.

    Every query below is scoped to ``student.id`` (or, for class-wide data
    such as exams and assignments, to the student's own
    ``academic_class_id``). No statistic here is derived from another
    student's records, which keeps this endpoint safe for student isolation.

    Marks/performance figures are produced by calling the existing
    ``get_student_performance`` service (and its underlying
    ``calculate_grade`` helper) instead of re-implementing the grading
    scale, per the project's existing grading convention.
    """

    # Reload the student with its academic class eagerly loaded.
    student = db.scalars(
        select(Student)
        .where(Student.id == student.id)
        .options(selectinload(Student.academic_class))
    ).one()

    academic_class_response = (
        ClassResponse.model_validate(student.academic_class)
        if student.academic_class
        else None
    )

    # --- Marks / academic performance (reuses existing grading logic) ---
    performance = get_student_performance(db, student.id)

    recent_marks = db.scalars(
        select(Mark)
        .where(Mark.student_id == student.id)
        .options(selectinload(Mark.subject))
        .order_by(Mark.id.desc())
        .limit(5)
    ).all()
    recent_mark_items = [
        StudentMarkItem(
            mark_id=mark.id,
            exam_id=mark.exam_id,
            subject_id=mark.subject_id,
            subject_name=mark.subject.name,
            marks=mark.marks,
            grade=calculate_grade(mark.marks),
        )
        for mark in recent_marks
    ]

    # --- Attendance (this student only) ---
    total_attendance_records = db.scalar(
        select(func.count())
        .select_from(Attendance)
        .where(Attendance.student_id == student.id)
    ) or 0
    present_attendance_records = db.scalar(
        select(func.count())
        .select_from(Attendance)
        .where(
            Attendance.student_id == student.id,
            Attendance.status == "present",
        )
    ) or 0
    absent_attendance_records = total_attendance_records - present_attendance_records
    attendance_percentage = _safe_percentage(
        present_attendance_records,
        total_attendance_records,
    )

    # --- Exams (student's academic class only) ---
    total_exams = 0
    past_exams_count = 0
    upcoming_exam_items: list[UpcomingExamItem] = []
    if student.academic_class_id is not None:
        total_exams = db.scalar(
            select(func.count())
            .select_from(Exam)
            .where(Exam.academic_class_id == student.academic_class_id)
        ) or 0

        upcoming_exams_count = db.scalar(
            select(func.count())
            .select_from(Exam)
            .where(
                Exam.academic_class_id == student.academic_class_id,
                Exam.exam_date >= date.today(),
            )
        ) or 0
        past_exams_count = total_exams - upcoming_exams_count

        upcoming_exams = db.scalars(
            select(Exam)
            .options(selectinload(Exam.academic_class))
            .where(
                Exam.academic_class_id == student.academic_class_id,
                Exam.exam_date >= date.today(),
            )
            .order_by(Exam.exam_date.asc(), Exam.id.asc())
            .limit(5)
        ).all()
        upcoming_exam_items = [
            UpcomingExamItem(
                id=exam.id,
                name=exam.name,
                exam_date=exam.exam_date,
                academic_class_name=(
                    exam.academic_class.name if exam.academic_class else None
                ),
            )
            for exam in upcoming_exams
        ]

    # --- Assignments (student's academic class; submissions scoped to this
    # student only) ---
    total_assignments = 0
    submitted_assignments = 0
    pending_assignments = 0
    if student.academic_class_id is not None:
        relevant_assignment_ids = select(Assignment.id).where(
            Assignment.academic_class_id == student.academic_class_id
        )

        total_assignments = db.scalar(
            select(func.count())
            .select_from(Assignment)
            .where(Assignment.academic_class_id == student.academic_class_id)
        ) or 0

        submitted_assignments = db.scalar(
            select(func.count(func.distinct(AssignmentSubmission.assignment_id)))
            .select_from(AssignmentSubmission)
            .where(
                AssignmentSubmission.student_id == student.id,
                AssignmentSubmission.assignment_id.in_(relevant_assignment_ids),
                AssignmentSubmission.status.in_(["submitted", "late"]),
            )
        ) or 0

        pending_assignments = total_assignments - submitted_assignments

    # --- Fees (this student only) ---
    total_fee_records = db.scalar(
        select(func.count()).select_from(Fee).where(Fee.student_id == student.id)
    ) or 0
    paid_fee_records = db.scalar(
        select(func.count())
        .select_from(Fee)
        .where(Fee.student_id == student.id, Fee.paid_amount >= Fee.amount)
    ) or 0
    pending_fee_records = total_fee_records - paid_fee_records

    total_fee_amount = float(
        db.scalar(
            select(func.coalesce(func.sum(Fee.amount), 0.0)).where(
                Fee.student_id == student.id
            )
        )
        or 0.0
    )
    paid_fee_amount = float(
        db.scalar(
            select(func.coalesce(func.sum(Fee.paid_amount), 0.0)).where(
                Fee.student_id == student.id
            )
        )
        or 0.0
    )
    due_fee_amount = round(total_fee_amount - paid_fee_amount, 2)

    return StudentDashboardResponse(
        student=StudentInfo.model_validate(student),
        academic_class=academic_class_response,
        total_results=performance.total_subjects,
        total_possible_marks=performance.total_marks,
        marks_obtained=performance.marks_obtained,
        percentage=performance.percentage,
        average_marks=performance.average_marks,
        overall_grade=performance.grade,
        recent_marks=recent_mark_items,
        total_attendance_records=total_attendance_records,
        present_attendance_records=present_attendance_records,
        absent_attendance_records=absent_attendance_records,
        attendance_percentage=attendance_percentage,
        total_exams=total_exams,
        upcoming_exams=upcoming_exam_items,
        past_exams_count=past_exams_count,
        total_assignments=total_assignments,
        submitted_assignments=submitted_assignments,
        pending_assignments=pending_assignments,
        total_fee_records=total_fee_records,
        paid_fee_records=paid_fee_records,
        pending_fee_records=pending_fee_records,
        total_fee_amount=round(total_fee_amount, 2),
        paid_fee_amount=round(paid_fee_amount, 2),
        due_fee_amount=due_fee_amount,
    )


def get_student_dashboard_overview(
    db: Session,
    student: Student,
) -> StudentDashboardOverviewResponse:
    dashboard = get_student_dashboard(db, student)
    partial_fee_records = db.scalar(
        select(func.count())
        .select_from(Fee)
        .where(
            Fee.student_id == student.id,
            Fee.paid_amount > 0,
            Fee.paid_amount < Fee.amount,
        )
    ) or 0

    return StudentDashboardOverviewResponse(
        student=dashboard.student,
        academic_class=dashboard.academic_class,
        total_marks_records=dashboard.total_results,
        total_marks_obtained=dashboard.marks_obtained,
        total_possible_marks=dashboard.total_possible_marks,
        percentage=dashboard.percentage,
        overall_grade=dashboard.overall_grade,
        total_attendance_records=dashboard.total_attendance_records,
        present_count=dashboard.present_attendance_records,
        absent_count=dashboard.absent_attendance_records,
        attendance_percentage=dashboard.attendance_percentage,
        total_assignments=dashboard.total_assignments,
        submitted_assignments=dashboard.submitted_assignments,
        pending_assignments=dashboard.pending_assignments,
        total_fee_records=dashboard.total_fee_records,
        total_fee_amount=dashboard.total_fee_amount,
        total_paid_amount=dashboard.paid_fee_amount,
        total_due_amount=dashboard.due_fee_amount,
        paid_fee_records=dashboard.paid_fee_records,
        partial_fee_records=partial_fee_records,
        pending_fee_records=dashboard.pending_fee_records - partial_fee_records,
        upcoming_exams=dashboard.upcoming_exams,
    )