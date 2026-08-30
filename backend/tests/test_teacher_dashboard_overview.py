import unittest
from datetime import date
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
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password


class TeacherDashboardOverviewApiTests(unittest.TestCase):
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

    def _suffix(self):
        return uuid4().hex[:8]

    def _create_user(self, role="teacher"):
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

    def _create_teacher(self):
        user = self._create_user()
        teacher = Teacher(
            user_id=user.id,
            name="Teacher One",
            email=f"teacher-profile-{self._suffix()}@example.com",
            phone="5557654321",
        )
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def _create_class(self):
        academic_class = AcademicClass(
            name="Computer Science 3",
            code=f"CS-{self._suffix()}",
            course="Computer Science",
            semester=3,
        )
        self.db.add(academic_class)
        self.db.commit()
        self.db.refresh(academic_class)
        return academic_class

    def _create_subject(self):
        subject = Subject(
            name="Mathematics",
            code=f"MATH-{self._suffix()}",
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_student(self, academic_class_id):
        student = Student(
            name="Student One",
            roll_number=f"ROLL-{self._suffix()}",
            email=f"student-{self._suffix()}@example.com",
            phone="5551234567",
            course="Computer Science",
            semester=3,
            academic_class_id=academic_class_id,
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _login(self, user):
        response = self.client.post(
            "/auth/login",
            json={"email": user.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_authenticated_teacher_response(self):
        teacher = self._create_teacher()
        self._login(teacher.user)

        response = self.client.get("/dashboard/teacher/overview")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["teacher"]["id"], teacher.id)

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get("/dashboard/teacher/overview")

        self.assertEqual(response.status_code, 401, response.text)

    def test_non_teacher_is_rejected(self):
        admin = self._create_user("admin")
        self._login(admin)

        response = self.client.get("/dashboard/teacher/overview")

        self.assertEqual(response.status_code, 403, response.text)

    def test_teacher_identity_is_returned(self):
        teacher = self._create_teacher()
        self._login(teacher.user)

        body = self.client.get("/dashboard/teacher/overview").json()["teacher"]

        self.assertEqual(body["id"], teacher.id)
        self.assertEqual(body["name"], teacher.name)
        self.assertEqual(body["email"], teacher.email)
        self.assertEqual(body["phone"], teacher.phone)

    def test_counts_are_scoped_to_assigned_classes_and_subjects(self):
        teacher = self._create_teacher()
        assigned_class = self._create_class()
        assigned_subject = self._create_subject()
        other_class = self._create_class()
        other_subject = self._create_subject()
        teacher.academic_classes.append(assigned_class)
        teacher.subjects.append(assigned_subject)
        self.db.commit()
        self._create_student(assigned_class.id)
        self._create_student(other_class.id)
        self._login(teacher.user)

        body = self.client.get("/dashboard/teacher/overview").json()

        self.assertEqual(body["total_assigned_classes"], 1)
        self.assertEqual(body["total_assigned_subjects"], 1)
        self.assertEqual(body["total_students"], 1)
        self.assertEqual(body["assigned_classes"][0]["id"], assigned_class.id)
        self.assertEqual(body["assigned_subjects"][0]["id"], assigned_subject.id)
        self.assertNotEqual(body["assigned_classes"][0]["id"], other_class.id)
        self.assertNotEqual(body["assigned_subjects"][0]["id"], other_subject.id)

    def test_assignment_submission_exam_and_attendance_statistics_are_scoped(self):
        teacher = self._create_teacher()
        academic_class = self._create_class()
        subject = self._create_subject()
        teacher.academic_classes.append(academic_class)
        teacher.subjects.append(subject)
        self.db.commit()
        student = self._create_student(academic_class.id)
        exam = Exam(
            name="Midterm",
            exam_type="midterm",
            exam_date=date(2026, 1, 15),
            academic_class_id=academic_class.id,
        )
        assignment = Assignment(
            title="Homework",
            description="Exercises",
            subject_id=subject.id,
            academic_class_id=academic_class.id,
            due_date=date(2026, 2, 1),
        )
        self.db.add_all([exam, assignment])
        self.db.commit()
        self.db.refresh(assignment)
        self.db.add_all(
            [
                AssignmentSubmission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    submitted_at=None,
                    status="pending",
                ),
                Attendance(
                    student_id=student.id,
                    attendance_date=date(2026, 1, 1),
                    status="present",
                ),
                Attendance(
                    student_id=student.id,
                    attendance_date=date(2026, 1, 2),
                    status="absent",
                ),
            ]
        )
        self.db.commit()
        self._login(teacher.user)

        body = self.client.get("/dashboard/teacher/overview").json()

        self.assertEqual(body["total_relevant_exams"], 1)
        self.assertEqual(body["total_assignments"], 1)
        self.assertEqual(body["total_submissions"], 1)
        self.assertEqual(body["pending_submissions"], 1)
        self.assertEqual(body["total_attendance_records"], 2)
        self.assertEqual(body["present_attendance_records"], 1)
        self.assertEqual(body["overall_attendance_percentage"], 50.0)

    def test_empty_teacher_data_is_zero_safe(self):
        teacher = self._create_teacher()
        self._login(teacher.user)

        body = self.client.get("/dashboard/teacher/overview").json()

        self.assertEqual(body["total_assigned_classes"], 0)
        self.assertEqual(body["total_assigned_subjects"], 0)
        self.assertEqual(body["total_students"], 0)
        self.assertEqual(body["total_relevant_exams"], 0)
        self.assertEqual(body["total_assignments"], 0)
        self.assertEqual(body["total_submissions"], 0)
        self.assertEqual(body["total_attendance_records"], 0)
        self.assertEqual(body["overall_attendance_percentage"], 0.0)
        self.assertEqual(body["assigned_classes"], [])
        self.assertEqual(body["assigned_subjects"], [])

    def test_response_shape_matches_teacher_dashboard_contract(self):
        teacher = self._create_teacher()
        self._login(teacher.user)

        response = self.client.get("/dashboard/teacher/overview")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            set(response.json()),
            {
                "teacher",
                "total_assigned_classes",
                "total_assigned_subjects",
                "total_students",
                "total_relevant_exams",
                "upcoming_exams",
                "total_assignments",
                "total_submissions",
                "submitted_submissions",
                "pending_submissions",
                "total_attendance_records",
                "present_attendance_records",
                "overall_attendance_percentage",
                "assigned_classes",
                "assigned_subjects",
            },
        )
