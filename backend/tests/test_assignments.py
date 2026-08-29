import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Assignment, Student, Subject, User
from app.security import hash_password


class AssignmentApiTests(unittest.TestCase):
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
        self.academic_class = self._create_academic_class()
        self.subject = self._create_subject(name="Mathematics", code="MATH-101")
        self.student = self._create_student()

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

    def _create_subject(self, **overrides) -> Subject:
        payload = {"name": "Subject", "code": "SUBJ-001"}
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_student(self, **overrides) -> Student:
        payload = {
            "name": "Ada Lovelace",
            "roll_number": "ROLL-001",
            "email": "ada@example.com",
            "phone": "5551234567",
            "course": "Computer Science",
            "semester": 3,
            "academic_class_id": self.academic_class.id,
        }
        payload.update(overrides)
        student = Student(**payload)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _create_assignment(self, **overrides) -> Assignment:
        payload = {
            "title": "Database Assignment 1",
            "description": "SQL normalization exercises",
            "subject_id": self.subject.id,
            "academic_class_id": self.academic_class.id,
            "due_date": date(2026, 9, 15),
        }
        payload.update(overrides)
        assignment = Assignment(**payload)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_create_assignment_successfully(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/assignments",
            json={
                "title": "Database Assignment 1",
                "description": "SQL normalization exercises",
                "subject_id": self.subject.id,
                "academic_class_id": self.academic_class.id,
                "due_date": "2026-09-15",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["title"], "Database Assignment 1")
        self.assertEqual(body["subject_id"], self.subject.id)
        self.assertEqual(body["academic_class_id"], self.academic_class.id)

    def test_create_assignment_missing_subject(self):
        self._login(self.admin.email)
        response = self.client.post(
            "/assignments",
            json={
                "title": "Missing subject assignment",
                "subject_id": 9999,
                "academic_class_id": self.academic_class.id,
                "due_date": "2026-09-15",
            },
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_create_assignment_missing_class(self):
        self._login(self.admin.email)
        response = self.client.post(
            "/assignments",
            json={
                "title": "Missing class assignment",
                "subject_id": self.subject.id,
                "academic_class_id": 9999,
                "due_date": "2026-09-15",
            },
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_create_assignment_invalid_required_fields(self):
        self._login(self.admin.email)
        response = self.client.post(
            "/assignments",
            json={
                "title": "",
                "subject_id": self.subject.id,
                "academic_class_id": self.academic_class.id,
                "due_date": "2026-09-15",
            },
        )
        self.assertEqual(response.status_code, 422, response.text)

    def test_get_assignment_successfully(self):
        assignment = self._create_assignment()
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments/{assignment.id}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], assignment.id)

    def test_get_missing_assignment(self):
        self._login(self.teacher.email)
        response = self.client.get("/assignments/9999")
        self.assertEqual(response.status_code, 404, response.text)

    def test_assignment_unauthenticated(self):
        response = self.client.get("/assignments")
        self.assertEqual(response.status_code, 401, response.text)

    def test_non_admin_cannot_create_assignment(self):
        self._login(self.teacher.email)
        response = self.client.post(
            "/assignments",
            json={
                "title": "Teacher Assignment",
                "subject_id": self.subject.id,
                "academic_class_id": self.academic_class.id,
                "due_date": "2026-09-15",
            },
        )
        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_update_assignment(self):
        assignment = self._create_assignment()
        self._login(self.teacher.email)
        response = self.client.patch(
            f"/assignments/{assignment.id}",
            json={"title": "Updated title"},
        )
        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_delete_assignment(self):
        assignment = self._create_assignment()
        self._login(self.teacher.email)
        response = self.client.delete(f"/assignments/{assignment.id}")
        self.assertEqual(response.status_code, 403, response.text)

    def test_admin_can_update_assignment(self):
        assignment = self._create_assignment()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/assignments/{assignment.id}",
            json={"title": "Updated assignment title"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["title"], "Updated assignment title")

    def test_partial_update_assignment(self):
        assignment = self._create_assignment()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/assignments/{assignment.id}",
            json={"description": "New description"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["description"], "New description")

    def test_update_assignment_missing_subject(self):
        assignment = self._create_assignment()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/assignments/{assignment.id}",
            json={"subject_id": 9999},
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_update_assignment_missing_class(self):
        assignment = self._create_assignment()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/assignments/{assignment.id}",
            json={"academic_class_id": 9999},
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_list_assignments(self):
        self._create_assignment(title="Alpha", due_date=date(2026, 1, 15))
        self._create_assignment(title="Beta", due_date=date(2026, 2, 15))
        self._login(self.teacher.email)
        response = self.client.get("/assignments")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total"], 2)
        self.assertEqual(len(body["items"]), 2)

    def test_search_assignment_title(self):
        self._create_assignment(title="Alpha assignment")
        self._login(self.teacher.email)
        response = self.client.get("/assignments?search=Alpha")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["title"], "Alpha assignment")

    def test_search_assignment_description(self):
        self._create_assignment(description="Normalization exercises")
        self._login(self.teacher.email)
        response = self.client.get("/assignments?search=Normalization")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_filter_assignments_by_subject(self):
        subject_2 = self._create_subject(name="Physics", code="PHYS-201")
        self._create_assignment(subject_id=self.subject.id)
        self._create_assignment(subject_id=subject_2.id)
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments?subject_id={self.subject.id}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_filter_assignments_by_class(self):
        academic_class_2 = self._create_academic_class(name="CS Semester 4", code="CS-4")
        self._create_assignment(academic_class_id=self.academic_class.id)
        self._create_assignment(academic_class_id=academic_class_2.id)
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments?academic_class_id={self.academic_class.id}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_filter_assignments_by_due_date(self):
        target = date(2026, 1, 15)
        self._create_assignment(title="A", due_date=target)
        self._create_assignment(title="B", due_date=date(2026, 2, 15))
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments?due_date={target.isoformat()}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_assignment_pagination(self):
        self._create_assignment(title="A", due_date=date(2026, 1, 15))
        self._create_assignment(title="B", due_date=date(2026, 2, 15))
        self._create_assignment(title="C", due_date=date(2026, 3, 15))
        self._login(self.teacher.email)
        response = self.client.get("/assignments?page=1&page_size=2")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["page_size"], 2)
        self.assertEqual(body["total"], 3)
        self.assertEqual(body["total_pages"], 2)

    def test_assignment_deterministic_ordering(self):
        self._create_assignment(title="Later", due_date=date(2026, 3, 15))
        self._create_assignment(title="Earlier", due_date=date(2026, 1, 15))
        self._login(self.teacher.email)
        response = self.client.get("/assignments")
        due_dates = [item["due_date"] for item in response.json()["items"]]
        self.assertEqual(due_dates, ["2026-01-15", "2026-03-15"])

    def test_delete_assignment(self):
        assignment = self._create_assignment()
        self._login(self.admin.email)
        response = self.client.delete(f"/assignments/{assignment.id}")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/assignments/{assignment.id}").status_code, 404)
