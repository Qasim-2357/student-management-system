import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Student, Teacher, User
from app.security import hash_password


class StudentApiTests(unittest.TestCase):
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
        return self.client.post("/students", json=self._student_payload(**overrides))

    def test_create_student(self):
        academic_class = AcademicClass(
            name="CS Semester 3",
            code="CS-3",
            course="Computer Science",
            semester=3,
        )
        self.db.add(academic_class)
        self.db.commit()
        student_user = self._create_user("student@example.com", "student")

        response = self._create_student_as_admin(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["roll_number"], "ROLL-001")
        self.assertEqual(response.json()["academic_class_id"], academic_class.id)

    def test_admin_user_cannot_be_linked_to_student(self):
        response = self._create_student_as_admin(user_id=self.admin.id)

        self.assertEqual(response.status_code, 422, response.text)

    def test_teacher_user_cannot_be_linked_to_student(self):
        response = self._create_student_as_admin(user_id=self.teacher.id)

        self.assertEqual(response.status_code, 422, response.text)

    def test_missing_user_cannot_be_linked_to_student(self):
        response = self._create_student_as_admin(user_id=9999)

        self.assertEqual(response.status_code, 422, response.text)

    def test_user_with_teacher_profile_cannot_be_linked_to_student(self):
        student_user = self._create_user("student@example.com", "student")
        teacher_profile = Teacher(
            user_id=student_user.id,
            name="Teacher Profile",
            email="teacher-profile@example.com",
            phone="5559999999",
        )
        self.db.add(teacher_profile)
        self.db.commit()

        response = self._create_student_as_admin(user_id=student_user.id)

        self.assertEqual(response.status_code, 409, response.text)

    def test_get_student(self):
        create_response = self._create_student_as_admin()
        student_id = create_response.json()["id"]

        response = self.client.get(f"/students/{student_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], student_id)

    def test_update_student(self):
        student_id = self._create_student_as_admin().json()["id"]

        response = self.client.patch(
            f"/students/{student_id}",
            json={"phone": "5550000000", "semester": 4},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["phone"], "5550000000")
        self.assertEqual(response.json()["semester"], 4)

    def test_update_rejects_non_student_user(self):
        student_id = self._create_student_as_admin().json()["id"]

        response = self.client.patch(
            f"/students/{student_id}",
            json={"user_id": self.admin.id},
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_delete_student(self):
        student_id = self._create_student_as_admin().json()["id"]

        response = self.client.delete(f"/students/{student_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/students/{student_id}").status_code, 404)

    def test_duplicate_roll_number(self):
        self.assertEqual(self._create_student_as_admin().status_code, 201)

        response = self.client.post(
            "/students",
            json=self._student_payload(email="second@example.com"),
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_duplicate_student_user_relationship(self):
        student_user = self._create_user("student@example.com", "student")
        self.assertEqual(
            self._create_student_as_admin(user_id=student_user.id).status_code,
            201,
        )

        response = self.client.post(
            "/students",
            json=self._student_payload(
                name="Grace Hopper",
                roll_number="ROLL-002",
                email="grace@example.com",
                user_id=student_user.id,
            ),
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_invalid_class(self):
        response = self._create_student_as_admin(academic_class_id=9999)

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_write(self):
        self._login(self.teacher.email)

        response = self.client.post("/students", json=self._student_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_authenticated_teacher_can_read_students(self):
        academic_class = AcademicClass(
            name="CS Semester 3",
            code="CS-3",
            course="Computer Science",
            semester=3,
        )
        self.db.add(academic_class)
        self.db.commit()
        teacher_profile = Teacher(
            user_id=self.teacher.id,
            name="Teacher One",
            email="teacher-profile@example.com",
            phone="5557654321",
        )
        teacher_profile.academic_classes.append(academic_class)
        self.db.add(teacher_profile)
        self.db.commit()
        self.assertEqual(
            self._create_student_as_admin(academic_class_id=academic_class.id).status_code,
            201,
        )
        self._login(self.teacher.email)

        response = self.client.get("/students")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_search(self):
        self.assertEqual(self._create_student_as_admin().status_code, 201)
        self.assertEqual(
            self.client.post(
                "/students",
                json=self._student_payload(
                    name="Grace Hopper",
                    roll_number="ROLL-002",
                    email="grace@example.com",
                ),
            ).status_code,
            201,
        )

        response = self.client.get("/students", params={"search": "grace"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["name"], "Grace Hopper")

    def test_filtering(self):
        academic_class = AcademicClass(
            name="CS Semester 3",
            code="CS-3",
            course="Computer Science",
            semester=3,
        )
        self.db.add(academic_class)
        self.db.commit()
        self.assertEqual(
            self._create_student_as_admin(academic_class_id=academic_class.id).status_code,
            201,
        )
        self.assertEqual(
            self.client.post(
                "/students",
                json=self._student_payload(
                    name="Grace Hopper",
                    roll_number="ROLL-002",
                    email="grace@example.com",
                    course="Mathematics",
                    semester=2,
                ),
            ).status_code,
            201,
        )

        response = self.client.get(
            "/students",
            params={
                "course": "Computer Science",
                "semester": 3,
                "academic_class_id": academic_class.id,
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["roll_number"], "ROLL-001")

    def test_pagination(self):
        for index in range(1, 4):
            response = self._create_student_as_admin(
                name=f"Student {index}",
                roll_number=f"ROLL-{index:03d}",
                email=f"student{index}@example.com",
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/students", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)
        self.assertEqual(response.json()["items"][0]["roll_number"], "ROLL-003")


if __name__ == "__main__":
    unittest.main()
