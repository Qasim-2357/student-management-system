import unittest
from datetime import date, timedelta
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
    User,
)
from app.security import hash_password


class StudentDashboardOverviewApiTests(unittest.TestCase):
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
        yield self.db

    def _suffix(self):
        return uuid4().hex[:8]

    def _user(self, role="student"):
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
            name="Computer Science 3",
            code=f"CS-{self._suffix()}",
            course="Computer Science",
            semester=3,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _student(self, user, academic_class_id=None):
        item = Student(
            user_id=user.id,
            name="Alice Student",
            roll_number=f"ROLL-{self._suffix()}",
            email=f"student-{self._suffix()}@example.com",
            phone="5551234567",
            course="Computer Science",
            semester=3,
            academic_class_id=academic_class_id,
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

    def test_successful_response_and_student_identity(self):
        user = self._user()
        student = self._student(user)
        self._login(user)

        response = self.client.get("/dashboard/student/overview")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["student"]["id"], student.id)
        self.assertEqual(response.json()["student"]["name"], student.name)

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get("/dashboard/student/overview")
        self.assertEqual(response.status_code, 401, response.text)

    def test_class_marks_attendance_assignments_and_fees(self):
        user = self._user()
        academic_class = self._class()
        student = self._student(user, academic_class.id)
        subject = Subject(name="Mathematics", code=f"MATH-{self._suffix()}")
        exam = Exam(
            name="Midterm",
            exam_type="exam",
            exam_date=date.today() + timedelta(days=5),
            academic_class_id=academic_class.id,
        )
        self.db.add_all([subject, exam])
        self.db.commit()
        mark = Mark(
            exam_id=exam.id,
            student_id=student.id,
            subject_id=subject.id,
            marks=80,
        )
        assignment = Assignment(
            title="Homework",
            description="Exercises",
            subject_id=subject.id,
            academic_class_id=academic_class.id,
            due_date=date.today() + timedelta(days=5),
        )
        self.db.add_all([mark, assignment])
        self.db.commit()
        self.db.refresh(assignment)
        self.db.add_all(
            [
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
                AssignmentSubmission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    status="submitted",
                ),
                Fee(student_id=student.id, amount=500, paid_amount=200, due_date=date.today()),
                Fee(student_id=student.id, amount=300, paid_amount=300, due_date=date.today()),
                Fee(student_id=student.id, amount=100, paid_amount=0, due_date=date.today()),
            ]
        )
        self.db.commit()
        self._login(user)

        body = self.client.get("/dashboard/student/overview").json()

        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["total_marks_records"], 1)
        self.assertEqual(body["total_marks_obtained"], 80)
        self.assertEqual(body["total_possible_marks"], 100)
        self.assertEqual(body["percentage"], 80)
        self.assertEqual(body["overall_grade"], "A")
        self.assertEqual(body["total_attendance_records"], 2)
        self.assertEqual(body["present_count"], 1)
        self.assertEqual(body["absent_count"], 1)
        self.assertEqual(body["attendance_percentage"], 50)
        self.assertEqual(body["total_assignments"], 1)
        self.assertEqual(body["submitted_assignments"], 1)
        self.assertEqual(body["pending_assignments"], 0)
        self.assertEqual(body["total_fee_records"], 3)
        self.assertEqual(body["total_fee_amount"], 900)
        self.assertEqual(body["total_paid_amount"], 500)
        self.assertEqual(body["total_due_amount"], 400)
        self.assertEqual(body["paid_fee_records"], 1)
        self.assertEqual(body["partial_fee_records"], 1)
        self.assertEqual(body["pending_fee_records"], 1)

    def test_empty_data_is_zero_safe(self):
        user = self._user()
        self._student(user)
        self._login(user)

        body = self.client.get("/dashboard/student/overview").json()

        self.assertIsNone(body["academic_class"])
        self.assertEqual(body["total_marks_records"], 0)
        self.assertEqual(body["total_possible_marks"], 0)
        self.assertEqual(body["total_marks_obtained"], 0)
        self.assertEqual(body["percentage"], 0)
        self.assertEqual(body["overall_grade"], "F")
        self.assertEqual(body["attendance_percentage"], 0)
        self.assertEqual(body["total_assignments"], 0)
        self.assertEqual(body["total_fee_records"], 0)
        self.assertEqual(body["total_due_amount"], 0)
        self.assertEqual(body["upcoming_exams"], [])

    def test_student_data_isolation(self):
        user_a = self._user()
        user_b = self._user()
        class_a = self._class()
        class_b = self._class()
        student_a = self._student(user_a, class_a.id)
        student_b = self._student(user_b, class_b.id)
        subject = Subject(name="Physics", code=f"PHY-{self._suffix()}")
        exam = Exam(
            name="Quiz",
            exam_type="quiz",
            exam_date=date.today() + timedelta(days=3),
            academic_class_id=class_b.id,
        )
        self.db.add_all([subject, exam])
        self.db.commit()
        self.db.add_all(
            [
                Mark(exam_id=exam.id, student_id=student_b.id, subject_id=subject.id, marks=99),
                Attendance(
                    student_id=student_b.id,
                    attendance_date=date(2026, 2, 1),
                    status="present",
                ),
                Fee(student_id=student_b.id, amount=999, paid_amount=0, due_date=date.today()),
            ]
        )
        self.db.commit()
        self._login(user_a)

        body = self.client.get("/dashboard/student/overview").json()

        self.assertEqual(body["student"]["id"], student_a.id)
        self.assertEqual(body["total_marks_records"], 0)
        self.assertEqual(body["total_attendance_records"], 0)
        self.assertEqual(body["total_fee_records"], 0)
        self.assertEqual(body["total_assignments"], 0)

    def test_response_shape(self):
        user = self._user()
        self._student(user)
        self._login(user)

        body = self.client.get("/dashboard/student/overview").json()

        self.assertEqual(
            set(body),
            {
                "student",
                "academic_class",
                "total_marks_records",
                "total_marks_obtained",
                "total_possible_marks",
                "percentage",
                "overall_grade",
                "total_attendance_records",
                "present_count",
                "absent_count",
                "attendance_percentage",
                "total_assignments",
                "submitted_assignments",
                "pending_assignments",
                "total_fee_records",
                "total_fee_amount",
                "total_paid_amount",
                "total_due_amount",
                "paid_fee_records",
                "partial_fee_records",
                "pending_fee_records",
                "upcoming_exams",
            },
        )
