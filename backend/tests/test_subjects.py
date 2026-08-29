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


class SubjectApiTests(unittest.TestCase):
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

    def _subject_payload(self, **overrides):
        payload = {
            "name": "Mathematics",
            "code": "MATH-101",
        }
        payload.update(overrides)
        return payload

    def _create_subject_as_admin(self, **overrides):
        self._login(self.admin.email)
        return self.client.post("/subjects", json=self._subject_payload(**overrides))

    # ---- create ----

    def test_create_subject(self):
        response = self._create_subject_as_admin()

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["name"], "Mathematics")
        self.assertEqual(response.json()["code"], "MATH-101")
        self.assertIn("id", response.json())

    def test_create_requires_name(self):
        self._login(self.admin.email)
        payload = self._subject_payload()
        del payload["name"]

        response = self.client.post("/subjects", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_code(self):
        self._login(self.admin.email)
        payload = self._subject_payload()
        del payload["code"]

        response = self.client.post("/subjects", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_rejects_blank_name(self):
        response = self._create_subject_as_admin(name="")

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_rejects_blank_code(self):
        response = self._create_subject_as_admin(code="")

        self.assertEqual(response.status_code, 422, response.text)

    def test_duplicate_subject_code(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)

        response = self.client.post(
            "/subjects",
            json=self._subject_payload(name="Applied Mathematics"),
        )

        self.assertEqual(response.status_code, 409, response.text)

    # ---- read ----

    def test_get_subject(self):
        create_response = self._create_subject_as_admin()
        subject_id = create_response.json()["id"]

        response = self.client.get(f"/subjects/{subject_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], subject_id)

    def test_get_subject_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/subjects/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_list_subjects(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)
        self._login(self.admin.email)

        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_authenticated_teacher_can_read_subjects(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)
        self._login(self.teacher_user.email)

        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_unauthenticated_read_rejected(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)
        self.client.cookies.clear()

        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 401, response.text)

    def test_unauthenticated_get_by_id_rejected(self):
        subject_id = self._create_subject_as_admin().json()["id"]
        self.client.cookies.clear()

        response = self.client.get(f"/subjects/{subject_id}")

        self.assertEqual(response.status_code, 401, response.text)

    # ---- update ----

    def test_update_subject(self):
        subject_id = self._create_subject_as_admin().json()["id"]

        response = self.client.patch(
            f"/subjects/{subject_id}",
            json={"name": "Advanced Mathematics", "code": "MATH-201"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "Advanced Mathematics")
        self.assertEqual(response.json()["code"], "MATH-201")

    def test_partial_update_name_only(self):
        subject_id = self._create_subject_as_admin().json()["id"]

        response = self.client.patch(
            f"/subjects/{subject_id}",
            json={"name": "Pure Mathematics"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "Pure Mathematics")
        self.assertEqual(response.json()["code"], "MATH-101")

    def test_partial_update_code_only(self):
        subject_id = self._create_subject_as_admin().json()["id"]

        response = self.client.patch(
            f"/subjects/{subject_id}",
            json={"code": "MATH-102"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["code"], "MATH-102")
        self.assertEqual(response.json()["name"], "Mathematics")

    def test_update_rejects_duplicate_code(self):
        self._create_subject_as_admin()
        second_subject_id = self._create_subject_as_admin(
            name="Physics",
            code="PHY-101",
        ).json()["id"]

        response = self.client.patch(
            f"/subjects/{second_subject_id}",
            json={"code": "MATH-101"},
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_update_same_code_on_same_subject_allowed(self):
        subject_id = self._create_subject_as_admin().json()["id"]

        response = self.client.patch(
            f"/subjects/{subject_id}",
            json={"code": "MATH-101", "name": "Mathematics (Renamed)"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], "Mathematics (Renamed)")
        self.assertEqual(response.json()["code"], "MATH-101")

    def test_update_not_found(self):
        self._login(self.admin.email)

        response = self.client.patch("/subjects/9999", json={"name": "Ghost Subject"})

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_update(self):
        subject_id = self._create_subject_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.patch(
            f"/subjects/{subject_id}",
            json={"name": "Hacked Subject"},
        )

        self.assertEqual(response.status_code, 403, response.text)

    # ---- delete ----

    def test_delete_subject(self):
        subject_id = self._create_subject_as_admin().json()["id"]

        response = self.client.delete(f"/subjects/{subject_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/subjects/{subject_id}").status_code, 404)

    def test_delete_not_found(self):
        self._login(self.admin.email)

        response = self.client.delete("/subjects/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_delete(self):
        subject_id = self._create_subject_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.delete(f"/subjects/{subject_id}")

        self.assertEqual(response.status_code, 403, response.text)

    def test_delete_blocked_by_related_marks_returns_conflict(self):
        subject_id = self._create_subject_as_admin().json()["id"]
        student_user = self._create_user("student@example.com", "student")
        student = Student(
            user_id=student_user.id,
            name="Ada Lovelace",
            roll_number="ROLL-001",
            email="ada@example.com",
            phone="5551234567",
            course="Computer Science",
            semester=3,
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)

        academic_class = AcademicClass(
            name="CS Semester 3",
            code="CS-3",
            course="Computer Science",
            semester=3,
        )
        self.db.add(academic_class)
        self.db.commit()
        self.db.refresh(academic_class)
        exam = Exam(
            name="Final",
            exam_type="final",
            exam_date=date(2026, 6, 1),
            academic_class_id=academic_class.id,
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        mark = Mark(
            exam_id=exam.id,
            student_id=student.id,
            subject_id=subject_id,
            marks=95.0,
        )
        self.db.add(mark)
        self.db.commit()

        self._login(self.admin.email)
        response = self.client.delete(f"/subjects/{subject_id}")

        self.assertEqual(response.status_code, 409, response.text)
        # The subject should still exist since the delete was rejected.
        self.assertEqual(self.client.get(f"/subjects/{subject_id}").status_code, 200)

    # ---- writes require admin ----

    def test_unauthorized_write(self):
        self._login(self.teacher_user.email)

        response = self.client.post("/subjects", json=self._subject_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_unauthenticated_write(self):
        response = self.client.post("/subjects", json=self._subject_payload())

        self.assertEqual(response.status_code, 401, response.text)

    # ---- search / pagination ----

    def test_search_by_name(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)
        self.assertEqual(
            self._create_subject_as_admin(name="Physics", code="PHY-101").status_code,
            201,
        )

        response = self.client.get("/subjects", params={"search": "physics"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["name"], "Physics")

    def test_search_by_code(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)

        response = self.client.get("/subjects", params={"search": "MATH-101"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_search_no_match(self):
        self.assertEqual(self._create_subject_as_admin().status_code, 201)

        response = self.client.get("/subjects", params={"search": "chemistry"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 0)
        self.assertEqual(response.json()["items"], [])

    def test_pagination(self):
        for index in range(1, 4):
            response = self._create_subject_as_admin(
                name=f"Subject {index}",
                code=f"SUB-{index:03d}",
            )
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/subjects", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_pagination_default_page_size(self):
        self._login(self.admin.email)
        for index in range(1, 4):
            self._create_subject_as_admin(
                name=f"Subject {index}",
                code=f"SUB-{index:03d}",
            )

        response = self.client.get("/subjects")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["page"], 1)
        self.assertEqual(response.json()["page_size"], 20)

    def test_pagination_page_size_maximum_enforced(self):
        self._login(self.admin.email)

        response = self.client.get("/subjects", params={"page_size": 101})

        self.assertEqual(response.status_code, 422, response.text)

    def test_pagination_deterministic_ordering(self):
        for index in range(1, 4):
            self._create_subject_as_admin(
                name=f"Subject {index}",
                code=f"SUB-{index:03d}",
            )

        first = self.client.get("/subjects")
        second = self.client.get("/subjects")

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