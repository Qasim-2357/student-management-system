import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Exam, Mark, Subject, Teacher, User
from app.security import hash_password


class StudentProfileApiTests(unittest.TestCase):
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
        self.teacher = self._create_user("teacher@example.com", "teacher")

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

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def _student_payload(self, **overrides):
        payload = {
            "name": "Ada Lovelace",
            "roll_number": "ROLL-001",
            "email": "ada@example.com",
            "phone": "5551234567",
            "date_of_birth": "2000-12-10",
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        return payload

    def _create_student_as_admin(self, **overrides):
        self._login(self.admin.email)
        response = self.client.post("/students", json=self._student_payload(**overrides))
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

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

    def _create_mark(self, student_id: int, subject_name: str, subject_code: str, marks: float) -> Mark:
        academic_class = self._create_academic_class(code=f"EXAM-{subject_code}")
        exam = Exam(
            name="Midterm",
            exam_type="midterm",
            exam_date=date(2026, 1, 15),
            academic_class_id=academic_class.id,
        )
        subject = Subject(name=subject_name, code=subject_code)
        self.db.add_all([exam, subject])
        self.db.commit()
        self.db.refresh(exam)
        self.db.refresh(subject)
        mark = Mark(
            exam_id=exam.id,
            student_id=student_id,
            subject_id=subject.id,
            marks=marks,
        )
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def test_successful_profile_retrieval(self):
        student = self._create_student_as_admin()

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["student"]["id"], student["id"])
        self.assertEqual(response.json()["student"]["name"], "Ada Lovelace")
        self.assertEqual(response.json()["student"]["roll_number"], "ROLL-001")

    def test_nonexistent_student_returns_404(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/profile")

        self.assertEqual(response.status_code, 404, response.text)

    def test_authenticated_access(self):
        academic_class = self._create_academic_class()
        teacher = Teacher(
            user_id=self.teacher.id,
            name="Teacher One",
            email="teacher-profile@example.com",
            phone="5557654321",
        )
        teacher.academic_classes.append(academic_class)
        self.db.add(teacher)
        self.db.commit()
        student = self._create_student_as_admin(academic_class_id=academic_class.id)
        self._login(self.teacher.email)

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)

    def test_unauthorized_access(self):
        student = self._create_student_as_admin()
        self.client.cookies.clear()

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 401, response.text)

    def test_student_with_academic_class(self):
        academic_class = self._create_academic_class()
        student = self._create_student_as_admin(academic_class_id=academic_class.id)

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsNotNone(response.json()["academic_class"])
        self.assertEqual(response.json()["academic_class"]["id"], academic_class.id)

    def test_student_without_academic_class(self):
        student = self._create_student_as_admin()

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsNone(response.json()["academic_class"])

    def test_student_with_marks(self):
        student = self._create_student_as_admin()
        mark = self._create_mark(student["id"], "Mathematics", "MATH-101", 87.5)

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(response.json()["marks"]), 1)
        self.assertEqual(response.json()["marks"][0]["id"], mark.id)
        self.assertEqual(response.json()["marks"][0]["marks"], 87.5)

    def test_student_without_marks(self):
        student = self._create_student_as_admin()

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["marks"], [])

    def test_correct_subject_information_for_marks(self):
        student = self._create_student_as_admin()
        mark = self._create_mark(student["id"], "Physics", "PHY-201", 91.0)

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        profile_mark = response.json()["marks"][0]
        self.assertEqual(profile_mark["subject_id"], mark.subject_id)
        self.assertEqual(profile_mark["subject_name"], "Physics")

    def test_correct_class_information(self):
        academic_class = self._create_academic_class(
            name="Math Semester 2",
            code="MATH-2",
            course="Mathematics",
            semester=2,
        )
        student = self._create_student_as_admin(academic_class_id=academic_class.id)

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        class_payload = response.json()["academic_class"]
        self.assertEqual(class_payload["name"], "Math Semester 2")
        self.assertEqual(class_payload["code"], "MATH-2")
        self.assertEqual(class_payload["course"], "Mathematics")
        self.assertEqual(class_payload["semester"], 2)

    def test_response_structure(self):
        student = self._create_student_as_admin()

        response = self.client.get(f"/students/{student['id']}/profile")

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"student", "academic_class", "marks"})
        self.assertEqual(
            set(payload["student"].keys()),
            {
                "id",
                "name",
                "roll_number",
                "email",
                "phone",
                "date_of_birth",
                "course",
                "semester",
            },
        )


if __name__ == "__main__":
    unittest.main()
