import unittest
from datetime import date, datetime, timedelta
from uuid import uuid4

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
    Attendance,
    Exam,
    Fee,
    Mark,
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password


class StudentAuthorizationApiTests(unittest.TestCase):
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

        class_a = self._class()
        class_b = self._class()
        user_a = self._user("student")
        user_b = self._user("student")
        self.student_a = self._student(user_a, class_a)
        self.student_b = self._student(user_b, class_b)
        subject_b = self._subject()
        exam_b = Exam(
            name="Exam B",
            exam_type="quiz",
            exam_date=date.today() + timedelta(days=5),
            academic_class_id=class_b.id,
        )
        assignment_b = Assignment(
            title="Assignment B",
            description="B",
            subject_id=subject_b.id,
            academic_class_id=class_b.id,
            due_date=date.today() + timedelta(days=5),
        )
        self.db.add_all([exam_b, assignment_b])
        self.db.commit()
        self.db.refresh(exam_b)
        self.db.refresh(assignment_b)
        self.mark_b = Mark(
            exam_id=exam_b.id,
            student_id=self.student_b.id,
            subject_id=subject_b.id,
            marks=88,
        )
        self.attendance_b = Attendance(
            student_id=self.student_b.id,
            attendance_date=date(2026, 1, 1),
            status="present",
        )
        self.fee_b = Fee(
            student_id=self.student_b.id,
            amount=100,
            paid_amount=0,
            due_date=date.today(),
        )
        self.submission_b = AssignmentSubmission(
            assignment_id=assignment_b.id,
            student_id=self.student_b.id,
            submitted_at=datetime.utcnow(),
            status="submitted",
        )
        self.db.add_all(
            [self.mark_b, self.attendance_b, self.fee_b, self.submission_b]
        )
        self.db.commit()
        for item in (self.mark_b, self.attendance_b, self.fee_b, self.submission_b):
            self.db.refresh(item)
        self.assignment_b = assignment_b
        self.user_a = user_a
        self.user_b = user_b

    def tearDown(self):
        self.client.close()
        self.db.close()
        app.dependency_overrides.clear()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def _override_db(self):
        yield self.db

    def _suffix(self):
        return uuid4().hex[:8]

    def _user(self, role):
        user = User(
            name=role.title(),
            email=f"{role}-{self._suffix()}@example.com",
            password_hash=hash_password("Password@123"),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _class(self):
        item = AcademicClass(
            name=f"Class {self._suffix()}",
            code=f"CLS-{self._suffix()}",
            course="Computer Science",
            semester=3,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _subject(self):
        item = Subject(name="Subject", code=f"SUB-{self._suffix()}")
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _student(self, user, academic_class):
        item = Student(
            user_id=user.id,
            name="Student",
            roll_number=f"ROLL-{self._suffix()}",
            email=f"student-{self._suffix()}@example.com",
            phone="5551234567",
            course="Computer Science",
            semester=3,
            academic_class_id=academic_class.id,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _login(self, user):
        response = self.client.post(
            "/auth/login",
            json={"email": user.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_student_cannot_access_another_students_student_reports(self):
        self._login(self.user_a)
        paths = [
            f"/students/{self.student_b.id}",
            f"/students/{self.student_b.id}/profile",
            f"/students/{self.student_b.id}/marksheet",
            f"/students/{self.student_b.id}/attendance-report",
            f"/students/{self.student_b.id}/report",
            f"/students/{self.student_b.id}/charts/marks",
            f"/students/{self.student_b.id}/charts/exams",
            f"/students/{self.student_b.id}/charts/attendance",
            f"/students/{self.student_b.id}/performance",
            f"/students/{self.student_b.id}/grades",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)

    def test_student_cannot_access_another_students_resource_records(self):
        self._login(self.user_a)
        paths = [
            f"/grades/{self.mark_b.id}",
            f"/fees/{self.fee_b.id}",
            f"/fees/{self.fee_b.id}/receipt",
            f"/fees/{self.fee_b.id}/receipt/pdf",
            f"/attendance/{self.attendance_b.id}",
            f"/submissions/{self.submission_b.id}",
            f"/assignments/{self.assignment_b.id}/submissions",
            f"/fees?student_id={self.student_b.id}",
            f"/attendance?student_id={self.student_b.id}",
            f"/marks?student_id={self.student_b.id}",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)

    def test_student_lists_are_scoped_when_no_student_id_is_supplied(self):
        self._login(self.user_a)
        for path in ("/fees", "/attendance", "/marks"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()["total"], 0)

    def test_admin_can_access_student_resources(self):
        admin = self._user("admin")
        self._login(admin)
        for path in (
            f"/students/{self.student_b.id}/profile",
            f"/grades/{self.mark_b.id}",
            f"/fees/{self.fee_b.id}",
            f"/attendance/{self.attendance_b.id}",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_authorized_teacher_can_access_assigned_student(self):
        teacher_user = self._user("teacher")
        teacher = Teacher(
            user_id=teacher_user.id,
            name="Teacher",
            email=f"teacher-profile-{self._suffix()}@example.com",
            phone="5557654321",
        )
        teacher.academic_classes.append(self.student_b.academic_class)
        self.db.add(teacher)
        self.db.commit()
        self._login(teacher_user)

        response = self.client.get(f"/students/{self.student_b.id}/profile")

        self.assertEqual(response.status_code, 200, response.text)

    def test_teacher_without_teacher_profile_is_not_granted_unscoped_access(self):
        teacher_user = self._user("teacher")
        self._login(teacher_user)

        for path in (
            f"/students/{self.student_b.id}",
            f"/students/{self.student_b.id}/profile",
            f"/grades/{self.mark_b.id}",
            f"/fees/{self.fee_b.id}",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)

    def test_unauthenticated_requests_remain_rejected(self):
        response = self.client.get(f"/students/{self.student_b.id}/profile")
        self.assertEqual(response.status_code, 401)
