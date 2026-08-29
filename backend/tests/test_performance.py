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


class PerformanceApiTests(unittest.TestCase):
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
        self.exam_1 = self._create_exam(name="Midterm", exam_date=date(2026, 1, 15))
        self.exam_2 = self._create_exam(name="Final", exam_date=date(2026, 6, 10))
        self.student = self._create_student()
        self.subject_1 = self._create_subject(name="Mathematics", code="MATH-101")
        self.subject_2 = self._create_subject(name="Physics", code="PHYS-201")
        self.subject_3 = self._create_subject(name="Chemistry", code="CHEM-301")

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
            "name": "Subject",
            "code": "SUBJ-001",
        }
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_mark(self, **overrides) -> Mark:
        payload = {
            "exam_id": self.exam_1.id,
            "student_id": self.student.id,
            "subject_id": self.subject_1.id,
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

    def test_get_student_performance_authenticated_success(self):
        self._create_mark(marks=85.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=90.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["total_marks"], 200)
        self.assertEqual(body["marks_obtained"], 175)
        self.assertEqual(body["percentage"], 87.5)
        self.assertEqual(body["average_marks"], 87.5)
        self.assertEqual(body["grade"], "A")
        self.assertEqual(body["total_subjects"], 2)
        self.assertEqual(len(body["results"]), 2)

    def test_get_student_performance_unauthenticated(self):
        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 401, response.text)

    def test_get_student_performance_student_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/performance")

        self.assertEqual(response.status_code, 404, response.text)

    def test_get_student_performance_no_marks(self):
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["total_marks"], 0)
        self.assertEqual(body["marks_obtained"], 0)
        self.assertEqual(body["percentage"], 0.0)
        self.assertEqual(body["average_marks"], 0.0)
        self.assertEqual(body["grade"], "F")
        self.assertEqual(body["total_subjects"], 0)
        self.assertEqual(body["results"], [])

    def test_get_student_performance_one_mark(self):
        self._create_mark(marks=75.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["marks_obtained"], 75.0)
        self.assertEqual(body["total_marks"], 100)
        self.assertEqual(body["percentage"], 75.0)
        self.assertEqual(body["average_marks"], 75.0)
        self.assertEqual(body["grade"], "B")
        self.assertEqual(body["results"][0]["grade"], "B")

    def test_get_student_performance_multiple_marks_calculates_statistics(self):
        self._create_mark(marks=80.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._create_mark(marks=70.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._create_mark(marks=60.0, subject_id=self.subject_3.id, exam_id=self.exam_2.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["marks_obtained"], 210.0)
        self.assertEqual(body["total_marks"], 300)
        self.assertEqual(body["percentage"], 70.0)
        self.assertEqual(body["average_marks"], 70.0)
        self.assertEqual(body["grade"], "B")
        self.assertEqual([item["grade"] for item in body["results"]], ["A", "B", "C"])

    def test_get_student_performance_orders_results_by_exam_then_mark(self):
        first_mark = self._create_mark(marks=90.0, subject_id=self.subject_1.id, exam_id=self.exam_2.id)
        second_mark = self._create_mark(marks=60.0, subject_id=self.subject_2.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        body = response.json()
        self.assertEqual([item["mark_id"] for item in body["results"]], [second_mark.id, first_mark.id])
        self.assertEqual([item["exam_id"] for item in body["results"]], [self.exam_1.id, self.exam_2.id])

    def test_get_student_performance_response_shape(self):
        self._create_mark(marks=85.0, subject_id=self.subject_1.id, exam_id=self.exam_1.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{self.student.id}/performance")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body.keys()), {
            "student_id",
            "total_marks",
            "marks_obtained",
            "percentage",
            "average_marks",
            "grade",
            "total_subjects",
            "results",
        })
        self.assertEqual(
            set(body["results"][0].keys()),
            {"mark_id", "exam_id", "subject_id", "marks", "grade"},
        )
