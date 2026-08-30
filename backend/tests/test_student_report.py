import unittest
from datetime import date, datetime
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
    User,
)
from app.security import hash_password


class StudentReportApiTests(unittest.TestCase):
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
        self.admin = self._create_user("admin@example.com", "admin")

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

    def _suffix(self) -> str:
        return uuid4().hex[:8]

    def _create_user(self, email: str, role: str) -> User:
        user = User(
            name=role.title(),
            email=email,
            password_hash=hash_password("Password@123"),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _create_class(self, **overrides) -> AcademicClass:
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

    def _create_student(self, **overrides) -> Student:
        payload = {
            "name": "Ada Lovelace",
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

    def _create_subject(self, **overrides) -> Subject:
        payload = {
            "name": "Mathematics",
            "code": f"MATH-{self._suffix()}",
        }
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_exam(self, academic_class_id: int, **overrides) -> Exam:
        payload = {
            "name": "Midterm",
            "exam_type": "midterm",
            "exam_date": date(2026, 1, 15),
            "academic_class_id": academic_class_id,
        }
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _login(self):
        response = self.client.post(
            "/auth/login",
            json={"email": self.admin.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_report_includes_existing_student_data(self):
        academic_class = self._create_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject()
        exam = self._create_exam(academic_class.id)
        self.db.add(Mark(exam_id=exam.id, student_id=student.id, subject_id=subject.id, marks=85))
        self.db.add(Attendance(student_id=student.id, attendance_date=date(2026, 1, 1), status="present"))
        self.db.add(Fee(student_id=student.id, amount=500, paid_amount=300, due_date=date(2026, 2, 1)))
        self.db.commit()
        self._login()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student.id)
        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["marks_summary"]["overall_grade"], "A")
        self.assertEqual(body["attendance"]["summary"]["attendance_percentage"], 100.0)
        self.assertEqual(body["fees"]["total_due_amount"], 200.0)

    def test_report_requires_authentication(self):
        student = self._create_student()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 401, response.text)

    def test_missing_student_returns_404(self):
        self._login()

        response = self.client.get("/students/9999/report")

        self.assertEqual(response.status_code, 404, response.text)

    def test_empty_report_is_zero_safe(self):
        student = self._create_student()
        self._login()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIsNone(body["academic_class"])
        self.assertEqual(body["marks"], [])
        self.assertEqual(body["attendance"]["records"], [])
        self.assertEqual(body["assignments"], [])
        self.assertEqual(body["fees"]["records"], [])
        self.assertEqual(body["marks_summary"]["total_possible_marks"], 0)
        self.assertEqual(body["marks_summary"]["percentage"], 0.0)
        self.assertEqual(body["marks_summary"]["overall_grade"], "F")
        self.assertEqual(body["attendance"]["summary"]["attendance_percentage"], 0.0)

    def test_report_calculates_marks_and_attendance(self):
        academic_class = self._create_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject_a = self._create_subject(name="Mathematics")
        subject_b = self._create_subject(name="Physics", code=f"PHYS-{self._suffix()}")
        exam = self._create_exam(academic_class.id)
        self.db.add_all(
            [
                Mark(exam_id=exam.id, student_id=student.id, subject_id=subject_a.id, marks=90),
                Mark(exam_id=exam.id, student_id=student.id, subject_id=subject_b.id, marks=70),
                Attendance(student_id=student.id, attendance_date=date(2026, 2, 1), status="present"),
                Attendance(student_id=student.id, attendance_date=date(2026, 2, 2), status="absent"),
                Attendance(student_id=student.id, attendance_date=date(2026, 2, 3), status="present"),
            ]
        )
        self.db.commit()
        self._login()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["marks_summary"]["total_marks_obtained"], 160.0)
        self.assertEqual(body["marks_summary"]["total_possible_marks"], 200)
        self.assertEqual(body["marks_summary"]["percentage"], 80.0)
        self.assertEqual(body["marks_summary"]["overall_grade"], "A")
        self.assertEqual(body["attendance"]["summary"]["total_records"], 3)
        self.assertEqual(body["attendance"]["summary"]["present_records"], 2)
        self.assertEqual(body["attendance"]["summary"]["absent_records"], 1)
        self.assertEqual(body["attendance"]["summary"]["attendance_percentage"], 66.67)
        self.assertEqual({item["grade"] for item in body["marks"]}, {"A+", "B"})

    def test_report_includes_assignments_submissions_and_fees(self):
        academic_class = self._create_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject()
        assignment = Assignment(
            title="Algebra Homework",
            description="Complete exercises",
            subject_id=subject.id,
            academic_class_id=academic_class.id,
            due_date=date(2026, 4, 1),
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        self.db.add(
            AssignmentSubmission(
                assignment_id=assignment.id,
                student_id=student.id,
                submitted_at=datetime(2026, 3, 31, 10, 0),
                status="submitted",
            )
        )
        self.db.add(Fee(student_id=student.id, amount=1000, paid_amount=250, due_date=date(2026, 5, 1)))
        self.db.commit()
        self._login()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body["assignments"]), 1)
        self.assertEqual(body["assignments"][0]["id"], assignment.id)
        self.assertEqual(body["assignments"][0]["submission"]["status"], "submitted")
        self.assertEqual(body["fees"]["total_amount"], 1000.0)
        self.assertEqual(body["fees"]["total_paid_amount"], 250.0)
        self.assertEqual(body["fees"]["total_due_amount"], 750.0)

    def test_report_has_deterministic_ordering_and_isolation(self):
        academic_class = self._create_class()
        student_a = self._create_student(academic_class_id=academic_class.id)
        student_b = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject()
        exam = self._create_exam(academic_class.id)
        self.db.add_all(
            [
                Attendance(student_id=student_a.id, attendance_date=date(2026, 6, 3), status="absent"),
                Attendance(student_id=student_a.id, attendance_date=date(2026, 6, 1), status="present"),
                Attendance(student_id=student_a.id, attendance_date=date(2026, 6, 2), status="present"),
                Mark(exam_id=exam.id, student_id=student_a.id, subject_id=subject.id, marks=95),
                Mark(exam_id=exam.id, student_id=student_b.id, subject_id=subject.id, marks=10),
            ]
        )
        self.db.commit()
        self._login()

        response = self.client.get(f"/students/{student_a.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(
            [record["attendance_date"] for record in body["attendance"]["records"]],
            ["2026-06-01", "2026-06-02", "2026-06-03"],
        )
        self.assertEqual(body["marks_summary"]["total_marks_obtained"], 95.0)
        self.assertEqual(len(body["marks"]), 1)

    def test_report_response_shape(self):
        student = self._create_student()
        self._login()

        response = self.client.get(f"/students/{student.id}/report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(
            set(body),
            {
                "student",
                "academic_class",
                "marks",
                "marks_summary",
                "attendance",
                "assignments",
                "fees",
            },
        )
        self.assertEqual(
            set(body["student"]),
            {"id", "name", "roll_number", "email", "phone", "course", "semester"},
        )
        self.assertEqual(
            set(body["attendance"]),
            {"summary", "records"},
        )
        self.assertEqual(
            set(body["fees"]),
            {"total_amount", "total_paid_amount", "total_due_amount", "records"},
        )
