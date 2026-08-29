import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, User
from app.security import hash_password


class ExamApiTests(unittest.TestCase):
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
        self.academic_class = self._create_academic_class()

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

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def _exam_payload(self, **overrides):
        payload = {
            "name": "Midterm",
            "exam_type": "midterm",
            "exam_date": "2026-01-15",
            "academic_class_id": self.academic_class.id,
        }
        payload.update(overrides)
        return payload

    def _create_exam_as_admin(self, **overrides):
        self._login(self.admin.email)
        return self.client.post("/exams", json=self._exam_payload(**overrides))

    # ---- create ----

    def test_create_exam(self):
        response = self._create_exam_as_admin()

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "Midterm")
        self.assertEqual(response.json()["exam_type"], "midterm")
        self.assertEqual(response.json()["exam_date"], "2026-01-15")
        self.assertEqual(response.json()["academic_class_id"], self.academic_class.id)

    def test_create_requires_name(self):
        self._login(self.admin.email)
        payload = self._exam_payload()
        del payload["name"]

        response = self.client.post("/exams", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_exam_type(self):
        self._login(self.admin.email)
        payload = self._exam_payload()
        del payload["exam_type"]

        response = self.client.post("/exams", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_exam_date(self):
        self._login(self.admin.email)
        payload = self._exam_payload()
        del payload["exam_date"]

        response = self.client.post("/exams", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_academic_class_id(self):
        self._login(self.admin.email)
        payload = self._exam_payload()
        del payload["academic_class_id"]

        response = self.client.post("/exams", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_rejects_missing_academic_class(self):
        response = self._create_exam_as_admin(academic_class_id=9999)

        self.assertEqual(response.status_code, 404, response.text)

    # ---- read ----

    def test_get_exam(self):
        create_response = self._create_exam_as_admin()
        exam_id = create_response.json()["id"]

        response = self.client.get(f"/exams/{exam_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], exam_id)

    def test_get_exam_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/exams/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_authenticated_teacher_can_read_exams(self):
        self.assertEqual(self._create_exam_as_admin().status_code, 201)
        self._login(self.teacher_user.email)

        response = self.client.get("/exams")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_unauthenticated_read_rejected(self):
        self.assertEqual(self._create_exam_as_admin().status_code, 201)
        self.client.cookies.clear()

        response = self.client.get("/exams")

        self.assertEqual(response.status_code, 401, response.text)

    def test_unauthenticated_get_by_id_rejected(self):
        exam_id = self._create_exam_as_admin().json()["id"]
        self.client.cookies.clear()

        response = self.client.get(f"/exams/{exam_id}")

        self.assertEqual(response.status_code, 401, response.text)

    # ---- update ----

    def test_update_exam(self):
        exam_id = self._create_exam_as_admin().json()["id"]

        response = self.client.patch(
            f"/exams/{exam_id}",
            json={"name": "Midterm (Rescheduled)", "exam_date": "2026-01-20"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "Midterm (Rescheduled)")
        self.assertEqual(response.json()["exam_date"], "2026-01-20")

    def test_partial_update_exam_type_only(self):
        exam_id = self._create_exam_as_admin().json()["id"]

        response = self.client.patch(
            f"/exams/{exam_id}",
            json={"exam_type": "final"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["exam_type"], "final")
        self.assertEqual(response.json()["name"], "Midterm")

    def test_update_rejects_missing_academic_class(self):
        exam_id = self._create_exam_as_admin().json()["id"]

        response = self.client.patch(
            f"/exams/{exam_id}",
            json={"academic_class_id": 9999},
        )

        self.assertEqual(response.status_code, 404, response.text)

    def test_update_to_valid_academic_class(self):
        exam_id = self._create_exam_as_admin().json()["id"]
        other_class = self._create_academic_class(
            name="Math Semester 2",
            code="MATH-2",
            course="Mathematics",
            semester=2,
        )

        response = self.client.patch(
            f"/exams/{exam_id}",
            json={"academic_class_id": other_class.id},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["academic_class_id"], other_class.id)

    def test_update_not_found(self):
        self._login(self.admin.email)

        response = self.client.patch("/exams/9999", json={"name": "Ghost Exam"})

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_update(self):
        exam_id = self._create_exam_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.patch(
            f"/exams/{exam_id}",
            json={"name": "Hacked Exam"},
        )

        self.assertEqual(response.status_code, 403, response.text)

    # ---- delete ----

    def test_delete_exam(self):
        exam_id = self._create_exam_as_admin().json()["id"]

        response = self.client.delete(f"/exams/{exam_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/exams/{exam_id}").status_code, 404)

    def test_delete_not_found(self):
        self._login(self.admin.email)

        response = self.client.delete("/exams/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_delete(self):
        exam_id = self._create_exam_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.delete(f"/exams/{exam_id}")

        self.assertEqual(response.status_code, 403, response.text)

    # ---- writes require admin ----

    def test_unauthorized_write(self):
        self._login(self.teacher_user.email)

        response = self.client.post("/exams", json=self._exam_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_unauthenticated_write(self):
        response = self.client.post("/exams", json=self._exam_payload())

        self.assertEqual(response.status_code, 401, response.text)

    # ---- search / filters / pagination ----

    def test_search_by_name(self):
        self.assertEqual(self._create_exam_as_admin().status_code, 201)
        self.assertEqual(
            self._create_exam_as_admin(name="Final Exam", exam_type="final").status_code,
            201,
        )

        response = self.client.get("/exams", params={"search": "final"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["name"], "Final Exam")

    def test_filter_by_academic_class_id(self):
        self.assertEqual(self._create_exam_as_admin().status_code, 201)
        other_class = self._create_academic_class(
            name="Math Semester 2",
            code="MATH-2",
            course="Mathematics",
            semester=2,
        )
        self.assertEqual(
            self._create_exam_as_admin(
                name="Math Final",
                academic_class_id=other_class.id,
            ).status_code,
            201,
        )

        response = self.client.get(
            "/exams", params={"academic_class_id": other_class.id}
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["academic_class_id"], other_class.id)

    def test_filter_by_exam_type(self):
        self.assertEqual(self._create_exam_as_admin(exam_type="midterm").status_code, 201)
        self.assertEqual(
            self._create_exam_as_admin(name="Final Exam", exam_type="final").status_code,
            201,
        )

        response = self.client.get("/exams", params={"exam_type": "final"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["exam_type"], "final")

    def test_pagination(self):
        for index in range(1, 4):
            response = self._create_exam_as_admin(
                name=f"Exam {index}",
                exam_date=f"2026-0{index}-15",
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/exams", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_pagination_deterministic_ordering(self):
        for index in range(1, 4):
            self._create_exam_as_admin(
                name=f"Exam {index}",
                exam_date=f"2026-0{index}-15",
            )

        first = self.client.get("/exams")
        second = self.client.get("/exams")

        self.assertEqual(
            [item["id"] for item in first.json()["items"]],
            [item["id"] for item in second.json()["items"]],
        )
        self.assertEqual(
            [item["exam_date"] for item in first.json()["items"]],
            sorted(item["exam_date"] for item in first.json()["items"]),
        )


if __name__ == "__main__":
    unittest.main()