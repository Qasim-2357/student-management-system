import unittest
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import Attendance, Student, User
from app.security import hash_password


class AttendanceReportApiTests(unittest.TestCase):
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

    def _create_attendance(
        self,
        student_id: int,
        attendance_date: date,
        status: str,
    ) -> Attendance:
        attendance = Attendance(
            student_id=student_id,
            attendance_date=attendance_date,
            status=status,
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def _login(self):
        response = self.client.post(
            "/auth/login",
            json={"email": self.admin.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_report(self):
        student = self._create_student()
        self._create_attendance(student.id, date(2026, 1, 2), "present")
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["student"]["id"], student.id)

    def test_report_requires_authentication(self):
        student = self._create_student()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 401, response.text)

    def test_missing_student_returns_404(self):
        self._login()

        response = self.client.get("/students/9999/attendance-report")

        self.assertEqual(response.status_code, 404, response.text)

    def test_student_with_no_records_returns_zero_safe_summary(self):
        student = self._create_student()
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(
            body["summary"],
            {
                "total_records": 0,
                "present_records": 0,
                "absent_records": 0,
                "attendance_percentage": 0.0,
            },
        )
        self.assertEqual(body["attendance_records"], [])

    def test_report_counts_records_and_calculates_percentage(self):
        student = self._create_student()
        self._create_attendance(student.id, date(2026, 1, 1), "present")
        self._create_attendance(student.id, date(2026, 1, 2), "present")
        self._create_attendance(student.id, date(2026, 1, 3), "absent")
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        summary = response.json()["summary"]
        self.assertEqual(summary["total_records"], 3)
        self.assertEqual(summary["present_records"], 2)
        self.assertEqual(summary["absent_records"], 1)
        self.assertEqual(summary["attendance_percentage"], 66.67)

    def test_report_returns_multiple_attendance_records(self):
        student = self._create_student()
        records = [
            self._create_attendance(student.id, date(2026, 2, 1), "present"),
            self._create_attendance(student.id, date(2026, 2, 2), "absent"),
        ]
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        returned = response.json()["attendance_records"]
        self.assertEqual(len(returned), 2)
        self.assertEqual({item["id"] for item in returned}, {record.id for record in records})

    def test_report_has_deterministic_date_ordering(self):
        student = self._create_student()
        self._create_attendance(student.id, date(2026, 3, 3), "absent")
        self._create_attendance(student.id, date(2026, 3, 1), "present")
        self._create_attendance(student.id, date(2026, 3, 2), "present")
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            [item["attendance_date"] for item in response.json()["attendance_records"]],
            ["2026-03-01", "2026-03-02", "2026-03-03"],
        )

    def test_report_response_shape(self):
        student = self._create_student()
        self._create_attendance(student.id, date(2026, 4, 1), "present")
        self._login()

        response = self.client.get(f"/students/{student.id}/attendance-report")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body), {"student", "summary", "attendance_records"})
        self.assertEqual(
            set(body["student"]),
            {"id", "name", "roll_number", "email", "phone", "course", "semester"},
        )
        self.assertEqual(
            set(body["summary"]),
            {
                "total_records",
                "present_records",
                "absent_records",
                "attendance_percentage",
            },
        )
        self.assertEqual(
            set(body["attendance_records"][0]),
            {"id", "student_id", "attendance_date", "status"},
        )

