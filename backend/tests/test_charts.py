import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Attendance, Exam, Mark, Student, Subject, User
from app.security import hash_password


class ChartsApiTests(unittest.TestCase):
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
        self.academic_class = self._create_academic_class()
        self.student = self._create_student()
        self.subject_1 = self._create_subject(name="Mathematics", code="MATH-101")
        self.subject_2 = self._create_subject(name="Programming", code="PROG-201")
        self.subject_3 = self._create_subject(name="Physics", code="PHYS-301")
        self.exam_1 = self._create_exam(name="Midterm", exam_date=date(2026, 1, 15))
        self.exam_2 = self._create_exam(name="Final", exam_date=date(2026, 6, 10))

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

    def _create_academic_class(self, **overrides) -> AcademicClass:
        payload = {
            "name": "CS Semester 3",
            "code": "CS-3",
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
            "roll_number": "ROLL-001",
            "email": "ada@example.com",
            "phone": "5551234567",
            "course": "Computer Science",
            "semester": 3,
            "academic_class_id": self.academic_class.id,
        }
        payload.update(overrides)
        student = Student(**payload)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _create_subject(self, **overrides) -> Subject:
        payload = {"name": "Subject", "code": "SUBJ-001"}
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_exam(self, **overrides) -> Exam:
        payload = {
            "name": "Exam",
            "exam_type": "midterm",
            "exam_date": date(2026, 1, 15),
            "academic_class_id": self.academic_class.id,
        }
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _create_mark(self, **overrides) -> Mark:
        payload = {
            "exam_id": self.exam_1.id,
            "student_id": self.student.id,
            "subject_id": self.subject_1.id,
            "marks": 80.0,
        }
        payload.update(overrides)
        mark = Mark(**payload)
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def _create_attendance(self, **overrides) -> Attendance:
        payload = {
            "student_id": self.student.id,
            "attendance_date": date(2026, 1, 10),
            "status": "present",
        }
        payload.update(overrides)
        attendance = Attendance(**payload)
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_marks_chart_success(self):
        self._create_mark(marks=80.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=85.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._create_mark(marks=90.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["data"][0]["subject_id"], self.subject_1.id)
        self.assertEqual(body["data"][0]["subject_name"], self.subject_1.name)
        self.assertEqual(body["data"][0]["average_marks"], 82.5)
        self.assertEqual(body["data"][1]["subject_id"], self.subject_2.id)
        self.assertEqual(body["data"][1]["subject_name"], self.subject_2.name)
        self.assertEqual(body["data"][1]["average_marks"], 90.0)

    def test_marks_chart_missing_student(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/charts/marks")

        self.assertEqual(response.status_code, 404, response.text)

    def test_marks_chart_unauthenticated(self):
        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 401, response.text)

    def test_marks_chart_no_marks(self):
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"], [])

    def test_marks_chart_multiple_marks_same_subject_are_averaged(self):
        self._create_mark(marks=70.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=90.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body["data"]), 1)
        self.assertEqual(body["data"][0]["average_marks"], 80.0)

    def test_marks_chart_rounding(self):
        self._create_mark(marks=80.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=81.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"][0]["average_marks"], 80.5)

    def test_marks_chart_deterministic_ordering(self):
        self._create_mark(marks=75.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._create_mark(marks=65.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()["data"]
        self.assertEqual([item["subject_id"] for item in data], [self.subject_1.id, self.subject_2.id])

    def test_marks_chart_response_shape(self):
        self._create_mark(marks=88.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/marks")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("student_id", body)
        self.assertIn("data", body)
        self.assertEqual(list(body["data"][0].keys()), ["subject_id", "subject_name", "average_marks"])

    def test_exams_chart_success(self):
        self._create_mark(marks=70.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=80.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._create_mark(marks=90.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._create_mark(marks=100.0, subject_id=self.subject_2.id, exam_id=self.exam_2.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["data"][0]["exam_id"], self.exam_1.id)
        self.assertEqual(body["data"][0]["exam_name"], self.exam_1.name)
        self.assertEqual(body["data"][0]["average_marks"], 75.0)
        self.assertEqual(body["data"][1]["exam_id"], self.exam_2.id)
        self.assertEqual(body["data"][1]["exam_name"], self.exam_2.name)
        self.assertEqual(body["data"][1]["average_marks"], 95.0)

    def test_exams_chart_missing_student(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/charts/exams")

        self.assertEqual(response.status_code, 404, response.text)

    def test_exams_chart_unauthenticated(self):
        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 401, response.text)

    def test_exams_chart_no_marks(self):
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"], [])

    def test_exams_chart_multiple_marks_same_exam_are_averaged(self):
        self._create_mark(marks=60.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=80.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body["data"]), 1)
        self.assertEqual(body["data"][0]["average_marks"], 70.0)

    def test_exams_chart_rounding(self):
        self._create_mark(marks=82.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=83.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"][0]["average_marks"], 82.5)

    def test_exams_chart_deterministic_ordering(self):
        self._create_mark(marks=50.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        self._create_mark(marks=60.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()["data"]
        self.assertEqual([item["exam_id"] for item in data], [self.exam_1.id, self.exam_2.id])

    def test_exams_chart_response_shape(self):
        self._create_mark(marks=88.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/exams")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("student_id", body)
        self.assertIn("data", body)
        self.assertEqual(list(body["data"][0].keys()), ["exam_id", "exam_name", "average_marks"])

    def test_attendance_chart_success(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 2), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 3), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 4), status="absent")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["present"], 2)
        self.assertEqual(body["absent"], 2)
        self.assertEqual(body["total"], 4)
        self.assertEqual(body["percentage"], 50.0)

    def test_attendance_chart_missing_student(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/charts/attendance")

        self.assertEqual(response.status_code, 404, response.text)

    def test_attendance_chart_unauthenticated(self):
        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 401, response.text)

    def test_attendance_chart_no_attendance(self):
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["present"], 0)
        self.assertEqual(body["absent"], 0)
        self.assertEqual(body["total"], 0)
        self.assertEqual(body["percentage"], 0.0)

    def test_attendance_chart_correct_present_count(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 2), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 3), status="present")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["present"], 2)

    def test_attendance_chart_correct_absent_count(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 2), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 3), status="absent")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["absent"], 2)

    def test_attendance_chart_correct_total(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 2), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 3), status="present")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)

    def test_attendance_chart_percentage_and_rounding(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 2), status="present")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 3), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 4), status="absent")
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 5), status="present")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["percentage"], 60.0)

    def test_attendance_chart_response_shape(self):
        self._create_attendance(student_id=self.student.id, attendance_date=date(2026, 1, 1), status="present")
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/charts/attendance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(
            list(body.keys()),
            ["student_id", "present", "absent", "total", "percentage"],
        )
