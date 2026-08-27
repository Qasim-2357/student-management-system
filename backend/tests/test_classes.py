import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, User
from app.security import hash_password


class ClassApiTests(unittest.TestCase):
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

    def _class_payload(self, **overrides):
        payload = {
            "name": "CS Semester 3",
            "code": "CS-3",
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        return payload

    def _create_class_as_admin(self, **overrides):
        self._login(self.admin.email)
        return self.client.post("/classes", json=self._class_payload(**overrides))

    # ---- create ----

    def test_create_class(self):
        response = self._create_class_as_admin()

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "CS Semester 3")
        self.assertEqual(response.json()["code"], "CS-3")
        self.assertEqual(response.json()["course"], "Computer Science")
        self.assertEqual(response.json()["semester"], 3)

    def test_create_requires_name(self):
        self._login(self.admin.email)
        payload = self._class_payload()
        del payload["name"]

        response = self.client.post("/classes", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_code(self):
        self._login(self.admin.email)
        payload = self._class_payload()
        del payload["code"]

        response = self.client.post("/classes", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_course(self):
        self._login(self.admin.email)
        payload = self._class_payload()
        del payload["course"]

        response = self.client.post("/classes", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_semester(self):
        self._login(self.admin.email)
        payload = self._class_payload()
        del payload["semester"]

        response = self.client.post("/classes", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_semester_must_be_positive(self):
        response = self._create_class_as_admin(semester=0)

        self.assertEqual(response.status_code, 422, response.text)

    def test_duplicate_class_code(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)

        response = self.client.post(
            "/classes",
            json=self._class_payload(name="CS Semester 3 (Section B)"),
        )

        self.assertEqual(response.status_code, 409, response.text)

    # ---- read ----

    def test_get_class(self):
        create_response = self._create_class_as_admin()
        class_id = create_response.json()["id"]

        response = self.client.get(f"/classes/{class_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], class_id)

    def test_get_class_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/classes/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_authenticated_teacher_can_read_classes(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)
        self._login(self.teacher_user.email)

        response = self.client.get("/classes")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_unauthenticated_read_rejected(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)
        self.client.cookies.clear()

        response = self.client.get("/classes")

        self.assertEqual(response.status_code, 401, response.text)

    def test_unauthenticated_get_by_id_rejected(self):
        class_id = self._create_class_as_admin().json()["id"]
        self.client.cookies.clear()

        response = self.client.get(f"/classes/{class_id}")

        self.assertEqual(response.status_code, 401, response.text)

    # ---- update ----

    def test_update_class(self):
        class_id = self._create_class_as_admin().json()["id"]

        response = self.client.patch(
            f"/classes/{class_id}",
            json={"name": "CS Semester 3 (Updated)", "semester": 4},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "CS Semester 3 (Updated)")
        self.assertEqual(response.json()["semester"], 4)

    def test_update_rejects_duplicate_code(self):
        self._create_class_as_admin()
        second_class_id = self._create_class_as_admin(
            name="Math Semester 2",
            code="MATH-2",
            course="Mathematics",
            semester=2,
        ).json()["id"]

        response = self.client.patch(
            f"/classes/{second_class_id}",
            json={"code": "CS-3"},
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_update_same_code_on_same_class_allowed(self):
        class_id = self._create_class_as_admin().json()["id"]

        response = self.client.patch(
            f"/classes/{class_id}",
            json={"code": "CS-3", "name": "CS Semester 3 (Renamed)"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "CS Semester 3 (Renamed)")

    def test_update_not_found(self):
        self._login(self.admin.email)

        response = self.client.patch("/classes/9999", json={"name": "Ghost Class"})

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_update(self):
        class_id = self._create_class_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.patch(
            f"/classes/{class_id}",
            json={"name": "Hacked Class"},
        )

        self.assertEqual(response.status_code, 403, response.text)

    # ---- delete ----

    def test_delete_class(self):
        class_id = self._create_class_as_admin().json()["id"]

        response = self.client.delete(f"/classes/{class_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/classes/{class_id}").status_code, 404)

    def test_delete_not_found(self):
        self._login(self.admin.email)

        response = self.client.delete("/classes/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_delete(self):
        class_id = self._create_class_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.delete(f"/classes/{class_id}")

        self.assertEqual(response.status_code, 403, response.text)

    # ---- writes require admin ----

    def test_unauthorized_write(self):
        self._login(self.teacher_user.email)

        response = self.client.post("/classes", json=self._class_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_unauthenticated_write(self):
        response = self.client.post("/classes", json=self._class_payload())

        self.assertEqual(response.status_code, 401, response.text)

    # ---- search / pagination ----

    def test_search_by_name(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)
        self.assertEqual(
            self._create_class_as_admin(
                name="Math Semester 2",
                code="MATH-2",
                course="Mathematics",
                semester=2,
            ).status_code,
            201,
        )

        response = self.client.get("/classes", params={"search": "math"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["name"], "Math Semester 2")

    def test_search_by_code(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)

        response = self.client.get("/classes", params={"search": "CS-3"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_search_by_course(self):
        self.assertEqual(self._create_class_as_admin().status_code, 201)

        response = self.client.get("/classes", params={"search": "computer science"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_pagination(self):
        for index in range(1, 4):
            response = self._create_class_as_admin(
                name=f"Class {index}",
                code=f"CLS-{index:03d}",
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/classes", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_pagination_deterministic_ordering(self):
        for index in range(1, 4):
            self._create_class_as_admin(
                name=f"Class {index}",
                code=f"CLS-{index:03d}",
            )

        first = self.client.get("/classes")
        second = self.client.get("/classes")

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