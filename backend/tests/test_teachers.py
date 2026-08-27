import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import Student, Teacher, User
from app.security import hash_password


class TeacherApiTests(unittest.TestCase):
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
        self.teacher_user = self._create_user("teacher@example.com", "teacher")

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

    def _teacher_payload(self, **overrides):
        payload = {
            "user_id": self.teacher_user.id,
            "name": "Ada Lovelace",
            "email": "ada.teacher@example.com",
            "phone": "5551234567",
        }
        payload.update(overrides)
        return payload

    def _create_teacher_as_admin(self, **overrides):
        self._login(self.admin.email)
        return self.client.post("/teachers", json=self._teacher_payload(**overrides))

    # ---- create ----

    def test_create_teacher(self):
        response = self._create_teacher_as_admin()

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "Ada Lovelace")
        self.assertEqual(response.json()["user_id"], self.teacher_user.id)
        self.assertEqual(response.json()["email"], "ada.teacher@example.com")

    def test_create_requires_user_id(self):
        self._login(self.admin.email)
        payload = self._teacher_payload()
        del payload["user_id"]

        response = self.client.post("/teachers", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_missing_user_cannot_be_linked_to_teacher(self):
        response = self._create_teacher_as_admin(user_id=9999)

        self.assertEqual(response.status_code, 422, response.text)

    def test_admin_user_cannot_be_linked_to_teacher(self):
        response = self._create_teacher_as_admin(user_id=self.admin.id)

        self.assertEqual(response.status_code, 422, response.text)

    def test_student_role_user_cannot_be_linked_to_teacher(self):
        student_role_user = self._create_user("student@example.com", "student")

        response = self._create_teacher_as_admin(user_id=student_role_user.id)

        self.assertEqual(response.status_code, 422, response.text)

    def test_user_with_student_profile_cannot_be_linked_to_teacher(self):
        # Create a user with teacher role but who already has a Student profile
        dual_user = self._create_user("dual@example.com", "teacher")
        student_profile = Student(
            user_id=dual_user.id,
            name="Student Profile",
            roll_number="ROLL-999",
            email="student-profile@example.com",
            phone="5558888888",
            course="Computer Science",
            semester=1,
        )
        self.db.add(student_profile)
        self.db.commit()

        response = self._create_teacher_as_admin(user_id=dual_user.id)

        self.assertEqual(response.status_code, 409, response.text)

    def test_duplicate_teacher_user_relationship(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)

        response = self.client.post(
            "/teachers",
            json=self._teacher_payload(
                name="Grace Hopper",
                email="grace.teacher@example.com",
                user_id=self.teacher_user.id,
            ),
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_duplicate_teacher_email(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)
        second_teacher_user = self._create_user("teacher2@example.com", "teacher")

        response = self.client.post(
            "/teachers",
            json=self._teacher_payload(
                name="Grace Hopper",
                user_id=second_teacher_user.id,
            ),
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_invalid_email_rejected(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/teachers",
            json=self._teacher_payload(email="not-an-email"),
        )

        self.assertEqual(response.status_code, 422, response.text)

    # ---- read ----

    def test_get_teacher(self):
        create_response = self._create_teacher_as_admin()
        teacher_id = create_response.json()["id"]

        response = self.client.get(f"/teachers/{teacher_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], teacher_id)

    def test_get_teacher_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/teachers/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_authenticated_teacher_can_read_teachers(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)
        self._login(self.teacher_user.email)

        response = self.client.get("/teachers")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_unauthenticated_read_rejected(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)
        self.client.cookies.clear()

        response = self.client.get("/teachers")

        self.assertEqual(response.status_code, 401, response.text)

    def test_unauthenticated_get_by_id_rejected(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]
        self.client.cookies.clear()

        response = self.client.get(f"/teachers/{teacher_id}")

        self.assertEqual(response.status_code, 401, response.text)

    # ---- update ----

    def test_update_teacher(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]

        response = self.client.patch(
            f"/teachers/{teacher_id}",
            json={"phone": "5550000000", "name": "Ada L."},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["phone"], "5550000000")
        self.assertEqual(response.json()["name"], "Ada L.")

    def test_update_rejects_non_teacher_user(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]

        response = self.client.patch(
            f"/teachers/{teacher_id}",
            json={"user_id": self.admin.id},
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_update_rejects_duplicate_email(self):
        self._create_teacher_as_admin()
        second_teacher_user = self._create_user("teacher2@example.com", "teacher")
        second_teacher_id = self._create_teacher_as_admin(
            name="Grace Hopper",
            email="grace.teacher@example.com",
            user_id=second_teacher_user.id,
        ).json()["id"]

        response = self.client.patch(
            f"/teachers/{second_teacher_id}",
            json={"email": "ada.teacher@example.com"},
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_update_rejects_user_already_linked_to_another_teacher(self):
        self._create_teacher_as_admin()
        second_teacher_user = self._create_user("teacher2@example.com", "teacher")
        second_teacher_id = self._create_teacher_as_admin(
            name="Grace Hopper",
            email="grace.teacher@example.com",
            user_id=second_teacher_user.id,
        ).json()["id"]

        response = self.client.patch(
            f"/teachers/{second_teacher_id}",
            json={"user_id": self.teacher_user.id},
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_unauthorized_update(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.patch(
            f"/teachers/{teacher_id}",
            json={"phone": "5550000000"},
        )

        self.assertEqual(response.status_code, 403, response.text)

    # ---- delete ----

    def test_delete_teacher(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]

        response = self.client.delete(f"/teachers/{teacher_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/teachers/{teacher_id}").status_code, 404)

    def test_unauthorized_delete(self):
        teacher_id = self._create_teacher_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.delete(f"/teachers/{teacher_id}")

        self.assertEqual(response.status_code, 403, response.text)

    # ---- writes require admin ----

    def test_unauthorized_write(self):
        self._login(self.teacher_user.email)

        response = self.client.post("/teachers", json=self._teacher_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_unauthenticated_write(self):
        response = self.client.post("/teachers", json=self._teacher_payload())

        self.assertEqual(response.status_code, 401, response.text)

    # ---- search / pagination ----

    def test_search_by_name(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)
        second_teacher_user = self._create_user("teacher2@example.com", "teacher")
        self.assertEqual(
            self._create_teacher_as_admin(
                name="Grace Hopper",
                email="grace.teacher@example.com",
                user_id=second_teacher_user.id,
            ).status_code,
            201,
        )

        response = self.client.get("/teachers", params={"search": "grace"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["name"], "Grace Hopper")

    def test_search_by_email(self):
        self.assertEqual(self._create_teacher_as_admin().status_code, 201)

        response = self.client.get("/teachers", params={"search": "ada.teacher"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_search_by_phone(self):
        self.assertEqual(self._create_teacher_as_admin(phone="5559990000").status_code, 201)

        response = self.client.get("/teachers", params={"search": "9990000"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_pagination(self):
        for index in range(1, 4):
            teacher_user = self._create_user(f"teacher{index}@example.com", "teacher")
            response = self._create_teacher_as_admin(
                name=f"Teacher {index}",
                email=f"teacher{index}@teachers.example.com",
                user_id=teacher_user.id,
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/teachers", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_pagination_deterministic_ordering(self):
        for index in range(1, 4):
            teacher_user = self._create_user(f"teacher{index}@example.com", "teacher")
            self._create_teacher_as_admin(
                name=f"Teacher {index}",
                email=f"teacher{index}@teachers.example.com",
                user_id=teacher_user.id,
            )

        first = self.client.get("/teachers")
        second = self.client.get("/teachers")

        self.assertEqual(
            [item["id"] for item in first.json()["items"]],
            [item["id"] for item in second.json()["items"]],
        )
        self.assertEqual(
            [item["id"] for item in first.json()["items"]],
            sorted(item["id"] for item in first.json()["items"]),
        )


if __name__ == "__main__":
    unittest.main()