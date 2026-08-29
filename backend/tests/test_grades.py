import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Exam, Mark, Student, Subject, User
from app.security import hash_password
from app.services.grades import calculate_grade


class CalculateGradeTests(unittest.TestCase):
    def test_100_is_a_plus(self):
        self.assertEqual(calculate_grade(100), "A+")

    def test_90_is_a_plus(self):
        self.assertEqual(calculate_grade(90), "A+")

    def test_89_99_is_a(self):
        self.assertEqual(calculate_grade(89.99), "A")

    def test_80_is_a(self):
        self.assertEqual(calculate_grade(80), "A")

    def test_79_99_is_b(self):
        self.assertEqual(calculate_grade(79.99), "B")

    def test_70_is_b(self):
        self.assertEqual(calculate_grade(70), "B")

    def test_69_99_is_c(self):
        self.assertEqual(calculate_grade(69.99), "C")

    def test_60_is_c(self):
        self.assertEqual(calculate_grade(60), "C")

    def test_59_99_is_d(self):
        self.assertEqual(calculate_grade(59.99), "D")

    def test_50_is_d(self):
        self.assertEqual(calculate_grade(50), "D")

    def test_49_99_is_f(self):
        self.assertEqual(calculate_grade(49.99), "F")

    def test_0_is_f(self):
        self.assertEqual(calculate_grade(0), "F")


class GradesApiTests(unittest.TestCase):
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
        self.exam = self._create_exam()
        self.student = self._create_student()
        self.subject = self._create_subject()

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

    def _create_student(self, **overrides) -> Student:
        payload = {
            "name": "Ada Lovelace",
            "roll_number": "ROLL-001",
            "email": "ada@example.com",
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
            "code": "MATH-101",
        }
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_mark(self, **overrides) -> Mark:
        payload = {
            "exam_id": self.exam.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "marks": 85.0,
        }
        payload.update(overrides)
        mark = Mark(**payload)
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    # ---- GET /grades/{mark_id} ----

    def test_get_mark_grade_success(self):
        mark = self._create_mark(marks=85.0)
        self._login(self.admin.email)

        response = self.client.get(f"/grades/{mark.id}")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["mark_id"], mark.id)
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["subject_id"], self.subject.id)
        self.assertEqual(body["exam_id"], self.exam.id)
        self.assertEqual(body["marks"], 85.0)
        self.assertEqual(body["grade"], "A")

    def test_get_mark_grade_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/grades/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_get_mark_grade_unauthenticated(self):
        mark = self._create_mark()

        response = self.client.get(f"/grades/{mark.id}")

        self.assertEqual(response.status_code, 401, response.text)

    def test_get_mark_grade_authenticated_non_admin(self):
        teacher_user = self._create_user("teacher@example.com", "teacher")
        mark = self._create_mark(marks=95.0)
        self._login(teacher_user.email)

        response = self.client.get(f"/grades/{mark.id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["grade"], "A+")

    def test_get_mark_grade_response_shape(self):
        mark = self._create_mark()
        self._login(self.admin.email)

        response = self.client.get(f"/grades/{mark.id}")

        self.assertEqual(
            set(response.json().keys()),
            {"mark_id", "student_id", "subject_id", "exam_id", "marks", "grade"},
        )

    # ---- GET /students/{student_id}/grades ----

    def test_get_student_grades_success(self):
        mark = self._create_mark(marks=72.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/grades")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(len(body["grades"]), 1)
        self.assertEqual(body["grades"][0]["mark_id"], mark.id)
        self.assertEqual(body["grades"][0]["grade"], "B")

    def test_get_student_grades_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/grades")

        self.assertEqual(response.status_code, 404, response.text)

    def test_get_student_grades_unauthenticated(self):
        response = self.client.get(f"/students/{self.student.id}/grades")

        self.assertEqual(response.status_code, 401, response.text)

    def test_get_student_grades_no_marks_returns_empty_list(self):
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/grades")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["grades"], [])

    def test_get_student_grades_multiple_marks(self):
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        other_exam = self._create_exam(
            name="Final", exam_type="final", exam_date=date(2026, 5, 1)
        )
        self._create_mark(marks=95.0)
        self._create_mark(subject_id=other_subject.id, marks=55.0)
        self._create_mark(exam_id=other_exam.id, marks=40.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/grades")

        self.assertEqual(response.status_code, 200, response.text)
        grades = response.json()["grades"]
        self.assertEqual(len(grades), 3)
        self.assertEqual({item["grade"] for item in grades}, {"A+", "D", "F"})

    def test_get_student_grades_deterministic_ordering(self):
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        other_exam = self._create_exam(
            name="Final", exam_type="final", exam_date=date(2026, 5, 1)
        )
        self._create_mark(marks=95.0)
        self._create_mark(subject_id=other_subject.id, marks=55.0)
        self._create_mark(exam_id=other_exam.id, marks=40.0)
        self._login(self.admin.email)

        first = self.client.get(f"/students/{self.student.id}/grades")
        second = self.client.get(f"/students/{self.student.id}/grades")

        self.assertEqual(first.json()["grades"], second.json()["grades"])
        exam_ids = [item["exam_id"] for item in first.json()["grades"]]
        self.assertEqual(exam_ids, sorted(exam_ids))

    def test_get_student_grades_response_shape(self):
        self._create_mark()
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/grades")

        body = response.json()
        self.assertEqual(set(body.keys()), {"student_id", "grades"})
        self.assertEqual(
            set(body["grades"][0].keys()),
            {"mark_id", "exam_id", "subject_id", "marks", "grade"},
        )


if __name__ == "__main__":
    unittest.main()