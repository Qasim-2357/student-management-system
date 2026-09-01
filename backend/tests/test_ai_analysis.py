import json
import unittest
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import (
    AcademicClass,
    Attendance,
    Exam,
    Mark,
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password
from app.services.ai_provider import AIProviderError

VALID_AI_PAYLOAD = json.dumps(
    {
        "summary": "The student is performing well overall.",
        "strengths": ["Strong in Mathematics"],
        "areas_for_improvement": ["Needs more consistency in Chemistry"],
        "recommendations": ["Review Chemistry fundamentals weekly"],
    }
)


class AIPerformanceAnalysisApiTests(unittest.TestCase):
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
        self.other_academic_class = self._create_academic_class(
            name="Other Class", code="OTHER-1"
        )
        self.exam = self._create_exam()
        self.subject = self._create_subject()

        self.student_user = self._create_user("student@example.com", "student")
        self.student = self._create_student(
            self.student_user, self.academic_class, roll_number="ROLL-A"
        )

        self.other_student_user = self._create_user(
            "other-student@example.com", "student"
        )
        self.other_student = self._create_student(
            self.other_student_user,
            self.other_academic_class,
            roll_number="ROLL-B",
            email="other-student@example.com",
        )

        self._create_mark(self.student, marks=85.0)
        self._create_attendance(self.student)

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

    def _create_exam(self, **overrides) -> Exam:
        payload = {
            "name": "Midterm",
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

    def _create_subject(self, **overrides) -> Subject:
        payload = {"name": "Mathematics", "code": "MATH-101"}
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_student(self, user, academic_class, **overrides) -> Student:
        payload = {
            "user_id": user.id,
            "academic_class_id": academic_class.id,
            "name": "Student",
            "roll_number": "ROLL-001",
            "email": "student@example.com",
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

    def _create_mark(self, student, **overrides) -> Mark:
        payload = {
            "exam_id": self.exam.id,
            "student_id": student.id,
            "subject_id": self.subject.id,
            "marks": 85.0,
        }
        payload.update(overrides)
        mark = Mark(**payload)
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def _create_attendance(self, student, **overrides) -> Attendance:
        payload = {
            "student_id": student.id,
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

    def _analysis_url(self, student_id: int) -> str:
        return f"/students/{student_id}/performance/analysis"

    # -- success cases -----------------------------------------------

    def test_admin_can_analyze_any_student(self):
        self._login(self.admin.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            return_value=VALID_AI_PAYLOAD,
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(
            set(body.keys()),
            {"summary", "strengths", "areas_for_improvement", "recommendations"},
        )
        self.assertEqual(body["summary"], "The student is performing well overall.")
        self.assertEqual(body["strengths"], ["Strong in Mathematics"])

    def test_student_can_analyze_own_data(self):
        self._login(self.student_user.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            return_value=VALID_AI_PAYLOAD,
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 200, response.text)

    def test_authorized_teacher_can_analyze_assigned_student(self):
        teacher_user = self._create_user("teacher@example.com", "teacher")
        teacher = Teacher(
            user_id=teacher_user.id,
            name="Teacher",
            email="teacher-profile@example.com",
            phone="5557654321",
        )
        teacher.academic_classes.append(self.academic_class)
        self.db.add(teacher)
        self.db.commit()

        self._login(teacher_user.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            return_value=VALID_AI_PAYLOAD,
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 200, response.text)

    # -- authorization failures ---------------------------------------

    def test_unauthenticated_access_is_rejected(self):
        response = self.client.get(self._analysis_url(self.student.id))
        self.assertEqual(response.status_code, 401)

    def test_student_cannot_analyze_another_student(self):
        self._login(self.student_user.email)

        response = self.client.get(self._analysis_url(self.other_student.id))

        self.assertEqual(response.status_code, 403)

    def test_unauthorized_teacher_cannot_analyze_unassigned_student(self):
        teacher_user = self._create_user("teacher2@example.com", "teacher")
        teacher = Teacher(
            user_id=teacher_user.id,
            name="Teacher 2",
            email="teacher2-profile@example.com",
            phone="5557654322",
        )
        # Intentionally not assigned to self.academic_class.
        teacher.academic_classes.append(self.other_academic_class)
        self.db.add(teacher)
        self.db.commit()

        self._login(teacher_user.email)

        response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 403)

    # -- not found ------------------------------------------------------

    def test_missing_student_returns_404(self):
        self._login(self.admin.email)

        response = self.client.get(self._analysis_url(999999))

        self.assertEqual(response.status_code, 404)

    # -- provider / response failure handling ---------------------------

    def test_ai_provider_failure_returns_503(self):
        self._login(self.admin.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            side_effect=AIProviderError("boom"),
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 503, response.text)

    def test_invalid_json_ai_response_returns_502(self):
        self._login(self.admin.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            return_value="not valid json at all",
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 502, response.text)

    def test_malformed_schema_ai_response_returns_502(self):
        self._login(self.admin.email)

        malformed_payload = json.dumps({"unexpected_key": "value"})

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            return_value=malformed_payload,
        ):
            response = self.client.get(self._analysis_url(self.student.id))

        self.assertEqual(response.status_code, 502, response.text)

    def test_ai_provider_is_never_called_for_unauthorized_requests(self):
        """Regression guard: an unauthorized caller must be rejected before
        any AI provider call would be attempted."""
        self._login(self.student_user.email)

        with patch(
            "app.services.ai_analysis.call_ai_provider",
            side_effect=AssertionError("AI provider should not have been called"),
        ):
            response = self.client.get(self._analysis_url(self.other_student.id))

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
