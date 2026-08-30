import unittest
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
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
    User,
)
from app.security import hash_password


class DashboardOverviewApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.Session = sessionmaker(bind=cls.engine, autocommit=False, autoflush=False)

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.db = self.Session()
        app.dependency_overrides[get_db] = self._override_db
        self.client = TestClient(app)
        self.admin = self._create_user("admin")

    def tearDown(self):
        self.client.close()
        self.db.close()
        app.dependency_overrides.clear()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def _override_db(self):
        try:
            yield self.db
        finally:
            pass

    def _suffix(self):
        return uuid4().hex[:8]

    def _create_user(self, role):
        user = User(
            name=role.title(),
            email=f"{role}-{self._suffix()}@example.com",
            password_hash=hash_password("Password@123"),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _create_class(self, **overrides):
        payload = {
            "name": "Computer Science 3",
            "code": f"CS-{self._suffix()}",
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        academic_class = AcademicClass(**payload)
        self.db.add(academic_class)
        self.db.commit()
        self.db.refresh(academic_class)
        return academic_class

    def _create_student(self, **overrides):
        payload = {
            "name": "Student",
            "roll_number": f"ROLL-{self._suffix()}",
            "email": f"student-{self._suffix()}@example.com",
            "phone": "5551234567",
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        student = Student(**payload)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _login(self, user):
        response = self.client.post(
            "/auth/login",
            json={"email": user.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_authenticated_overview(self):
        self._login(self.admin)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total_students"], 0)

    def test_overview_requires_authentication(self):
        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 401, response.text)

    def test_overview_is_admin_only(self):
        teacher = self._create_user("teacher")
        self._login(teacher)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 403, response.text)

    def test_overview_returns_all_statistics(self):
        academic_class = self._create_class()
        subject = Subject(name="Mathematics", code=f"MATH-{self._suffix()}")
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        teacher_user = self._create_user("teacher")
        teacher = Teacher(
            user_id=teacher_user.id,
            name="Teacher",
            email=f"teacher-profile-{self._suffix()}@example.com",
            phone="5557654321",
        )
        student = self._create_student(
            academic_class_id=academic_class.id,
            course="Computer Science",
        )
        exam = Exam(
            name="Midterm",
            exam_type="midterm",
            exam_date=date(2026, 1, 15),
            academic_class_id=academic_class.id,
        )
        assignment = Assignment(
            title="Homework",
            description="Exercises",
            subject_id=subject.id,
            academic_class_id=academic_class.id,
            due_date=date(2026, 2, 1),
        )
        self.db.add_all([teacher, exam, assignment])
        self.db.commit()
        self.db.refresh(exam)
        self.db.refresh(assignment)
        self.db.add_all(
            [
                Mark(
                    exam_id=exam.id,
                    student_id=student.id,
                    subject_id=subject.id,
                    marks=80,
                ),
                Attendance(
                    student_id=student.id,
                    attendance_date=date(2026, 1, 1),
                    status="present",
                ),
                Attendance(
                    student_id=student.id,
                    attendance_date=date(2026, 1, 2),
                    status="absent",
                ),
                AssignmentSubmission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    submitted_at=None,
                    status="pending",
                ),
                Fee(
                    student_id=student.id,
                    amount=1000,
                    paid_amount=400,
                    due_date=date(2026, 3, 1),
                ),
            ]
        )
        self.db.commit()
        self._login(self.admin)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_students"], 1)
        self.assertEqual(body["total_teachers"], 1)
        self.assertEqual(body["total_classes"], 1)
        self.assertEqual(body["total_subjects"], 1)
        self.assertEqual(body["total_exams"], 1)
        self.assertEqual(body["total_marks_records"], 1)
        self.assertEqual(body["total_attendance_records"], 2)
        self.assertEqual(body["present_count"], 1)
        self.assertEqual(body["absent_count"], 1)
        self.assertEqual(body["attendance_percentage"], 50.0)
        self.assertEqual(body["total_assignments"], 1)
        self.assertEqual(body["total_submissions"], 1)
        self.assertEqual(body["total_fee_records"], 1)
        self.assertEqual(body["total_fee_amount"], 1000.0)
        self.assertEqual(body["total_paid_amount"], 400.0)
        self.assertEqual(body["total_due_amount"], 600.0)
        self.assertEqual(
            body["students_by_course"],
            [{"course": "Computer Science", "count": 1}],
        )

    def test_overview_aggregates_multiple_students_by_course(self):
        self._create_student(course="Computer Science")
        self._create_student(course="Computer Science")
        self._create_student(course="Mathematics")
        self._login(self.admin)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_students"], 3)
        self.assertEqual(
            body["students_by_course"],
            [
                {"course": "Computer Science", "count": 2},
                {"course": "Mathematics", "count": 1},
            ],
        )

    def test_overview_is_zero_safe(self):
        self._login(self.admin)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["attendance_percentage"], 0.0)
        self.assertEqual(body["total_fee_amount"], 0.0)
        self.assertEqual(body["total_paid_amount"], 0.0)
        self.assertEqual(body["total_due_amount"], 0.0)
        self.assertEqual(body["students_by_course"], [])

    def test_overview_response_shape(self):
        self._login(self.admin)

        response = self.client.get("/dashboard/overview")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            set(response.json()),
            {
                "total_students",
                "students_by_course",
                "total_teachers",
                "total_classes",
                "total_subjects",
                "total_exams",
                "total_marks_records",
                "total_attendance_records",
                "present_count",
                "absent_count",
                "attendance_percentage",
                "total_assignments",
                "total_submissions",
                "total_fee_records",
                "total_fee_amount",
                "total_paid_amount",
                "total_due_amount",
            },
        )
