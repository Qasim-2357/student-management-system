import unittest
from datetime import date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import (
    AcademicClass,
    Assignment,
    AssignmentSubmission,
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password


class SubmissionApiTests(unittest.TestCase):
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
        self.teacher_profile = Teacher(
            user_id=self.teacher.id,
            name="Teacher One",
            email="teacher-profile@example.com",
            phone="5557654321",
        )
        self.db.add(self.teacher_profile)
        self.db.commit()
        self.db.refresh(self.teacher_profile)

        self.academic_class = self._create_academic_class()
        self.subject = self._create_subject(name="Mathematics", code="MATH-101")
        self.teacher_profile.academic_classes.append(self.academic_class)
        self.teacher_profile.subjects.append(self.subject)
        self.db.commit()

        self.student_1 = self._create_student(name="Ada Lovelace", roll_number="ROLL-001")
        self.student_2 = self._create_student(name="Grace Hopper", roll_number="ROLL-002")
        self.assignment = self._create_assignment(
            title="Database Assignment 1",
            description="Normalization exercises",
            due_date=date(2026, 9, 15),
        )

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
            "name": "Student",
            "roll_number": "ROLL-001",
            "email": "student@example.com",
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
            "description": "SQL exercises",
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

    def _create_submission(self, **overrides) -> AssignmentSubmission:
        payload = {
            "assignment_id": self.assignment.id,
            "student_id": self.student_1.id,
            "submitted_at": datetime(2026, 9, 14, 15, 30),
            "status": "submitted",
        }
        payload.update(overrides)
        submission = AssignmentSubmission(**payload)
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_create_pending_submission(self):
        self._login(self.admin.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": self.student_1.id, "submitted_at": None},
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "pending")

    def test_create_on_time_submission(self):
        self._login(self.admin.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": self.student_1.id, "submitted_at": "2026-09-14T15:30:00"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "submitted")

    def test_create_late_submission(self):
        self._login(self.admin.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": self.student_1.id, "submitted_at": "2026-09-16T15:30:00"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "late")

    def test_create_submission_missing_assignment(self):
        self._login(self.admin.email)
        response = self.client.post(
            "/assignments/9999/submissions",
            json={"student_id": self.student_1.id},
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_create_submission_missing_student(self):
        self._login(self.admin.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": 9999},
        )
        self.assertEqual(response.status_code, 404, response.text)

    def test_duplicate_submission_raises_conflict(self):
        self._create_submission()
        self._login(self.admin.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": self.student_1.id, "submitted_at": "2026-09-15T10:00:00"},
        )
        self.assertEqual(response.status_code, 409, response.text)

    def test_get_submission(self):
        submission = self._create_submission()
        self._login(self.teacher.email)
        response = self.client.get(f"/submissions/{submission.id}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], submission.id)

    def test_get_missing_submission(self):
        self._login(self.teacher.email)
        response = self.client.get("/submissions/9999")
        self.assertEqual(response.status_code, 404, response.text)

    def test_submission_unauthenticated(self):
        response = self.client.get(f"/assignments/{self.assignment.id}/submissions")
        self.assertEqual(response.status_code, 401, response.text)

    def test_invalid_submission_status_is_rejected(self):
        self._login(self.admin.email)
        response = self.client.get(
            f"/assignments/{self.assignment.id}/submissions?status=invalid-status"
        )
        self.assertEqual(response.status_code, 422, response.text)

    def test_non_admin_cannot_create_submission(self):
        self._login(self.teacher.email)
        response = self.client.post(
            f"/assignments/{self.assignment.id}/submissions",
            json={"student_id": self.student_1.id},
        )
        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_update_submission(self):
        submission = self._create_submission()
        self._login(self.teacher.email)
        response = self.client.patch(
            f"/submissions/{submission.id}",
            json={"submitted_at": "2026-09-17T12:00:00"},
        )
        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_delete_submission(self):
        submission = self._create_submission()
        self._login(self.teacher.email)
        response = self.client.delete(f"/submissions/{submission.id}")
        self.assertEqual(response.status_code, 403, response.text)

    def test_admin_can_update_submission(self):
        submission = self._create_submission()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/submissions/{submission.id}",
            json={"submitted_at": "2026-09-16T12:00:00"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "late")

    def test_update_submitted_at_changes_status(self):
        submission = self._create_submission(submitted_at=datetime(2026, 9, 16, 12, 0), status="late")
        self._login(self.admin.email)
        response = self.client.patch(
            f"/submissions/{submission.id}",
            json={"submitted_at": "2026-09-14T12:00:00"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "submitted")

    def test_update_student(self):
        submission = self._create_submission()
        self._login(self.admin.email)
        response = self.client.patch(
            f"/submissions/{submission.id}",
            json={"student_id": self.student_2.id},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["student_id"], self.student_2.id)

    def test_duplicate_student_assignment_on_update_raises_conflict(self):
        self._create_submission(student_id=self.student_1.id)
        duplicate = self._create_submission(student_id=self.student_2.id)
        self._login(self.admin.email)
        response = self.client.patch(
            f"/submissions/{duplicate.id}",
            json={"student_id": self.student_1.id},
        )
        self.assertEqual(response.status_code, 409, response.text)

    def test_list_submissions(self):
        self._create_submission(student_id=self.student_1.id)
        self._create_submission(student_id=self.student_2.id, submitted_at=None, status="pending")
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments/{self.assignment.id}/submissions")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total"], 2)
        self.assertEqual(len(body["items"]), 2)

    def test_filter_submissions_by_student(self):
        self._create_submission(student_id=self.student_1.id)
        self._create_submission(student_id=self.student_2.id, submitted_at=None, status="pending")
        self._login(self.teacher.email)
        response = self.client.get(
            f"/assignments/{self.assignment.id}/submissions?student_id={self.student_1.id}"
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_filter_submissions_by_status(self):
        self._create_submission(student_id=self.student_1.id)
        self._create_submission(student_id=self.student_2.id, submitted_at=None, status="pending")
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments/{self.assignment.id}/submissions?status=pending")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_submission_pagination(self):
        self._create_submission(student_id=self.student_1.id)
        self._create_submission(student_id=self.student_2.id, submitted_at=None, status="pending")
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments/{self.assignment.id}/submissions?page=1&page_size=1")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["page_size"], 1)
        self.assertEqual(body["total"], 2)
        self.assertEqual(body["total_pages"], 2)

    def test_submission_deterministic_ordering(self):
        self._create_submission(student_id=self.student_2.id)
        self._create_submission(student_id=self.student_1.id)
        self._login(self.teacher.email)
        response = self.client.get(f"/assignments/{self.assignment.id}/submissions")
        student_ids = [item["student_id"] for item in response.json()["items"]]
        self.assertEqual(student_ids, [self.student_1.id, self.student_2.id])

    def test_delete_submission(self):
        submission = self._create_submission()
        self._login(self.admin.email)
        response = self.client.delete(f"/submissions/{submission.id}")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/submissions/{submission.id}").status_code, 404)

    def test_submission_status_recalculates_if_assignment_due_date_changes(self):
        submission = self._create_submission(submitted_at=datetime(2026, 9, 16, 12, 0), status="late")
        self._login(self.admin.email)
        response = self.client.patch(
            f"/assignments/{self.assignment.id}",
            json={"due_date": "2026-09-20"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        refreshed = self.client.get(f"/submissions/{submission.id}")
        self.assertEqual(refreshed.status_code, 200, refreshed.text)
        self.assertEqual(refreshed.json()["status"], "submitted")
