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
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password


class DashboardApiTests(unittest.TestCase):
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

    def _unique_suffix(self) -> str:
        return uuid4().hex[:8]

    def _create_user(self, email: str | None = None, role: str = "admin") -> User:
        user_email = email or f"{role}-{self._unique_suffix()}@example.com"
        user = User(
            name=role.title(),
            email=user_email,
            password_hash=hash_password("Password@123"),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _create_admin(self) -> User:
        return self._create_user(email=f"admin-{self._unique_suffix()}@example.com", role="admin")

    def _create_academic_class(self, **overrides) -> AcademicClass:
        payload = {
            "name": "CS Semester 3",
            "code": f"CS-{self._unique_suffix()}",
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        academic_class = AcademicClass(**payload)
        self.db.add(academic_class)
        self.db.commit()
        self.db.refresh(academic_class)
        return academic_class

    def _create_student(self, **overrides) -> Student:
        payload = {
            "name": "Ada Lovelace",
            "roll_number": f"ROLL-{self._unique_suffix()}",
            "email": f"ada-{self._unique_suffix()}@example.com",
            "phone": "5551234567",
            "course": "Computer Science",
            "semester": 3,
        }
        if "academic_class_id" not in overrides:
            payload["academic_class_id"] = self._create_academic_class().id
        payload.update(overrides)
        student = Student(**payload)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _create_teacher(self, **overrides) -> Teacher:
        if "user_id" not in overrides:
            user = self._create_user(role="teacher")
            overrides["user_id"] = user.id
        payload = {
            "name": "Teacher One",
            "email": f"teacher-{self._unique_suffix()}@example.com",
            "phone": "5557654321",
        }
        payload.update(overrides)
        teacher = Teacher(**payload)
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def _create_subject(self, **overrides) -> Subject:
        payload = {"name": "Mathematics", "code": f"MATH-{self._unique_suffix()}"}
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _create_exam(self, **overrides) -> Exam:
        payload = {
            "name": "Midterm",
            "exam_type": "midterm",
            "exam_date": date.today() + timedelta(days=30),
        }
        if "academic_class_id" not in overrides:
            payload["academic_class_id"] = self._create_academic_class().id
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _create_assignment(self, **overrides) -> Assignment:
        payload = {
            "title": "Assignment 1",
            "description": "Solve the questions",
            "due_date": date.today() + timedelta(days=20),
        }
        if "subject_id" not in overrides:
            payload["subject_id"] = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}").id
        if "academic_class_id" not in overrides:
            payload["academic_class_id"] = self._create_academic_class().id
        payload.update(overrides)
        assignment = Assignment(**payload)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def _create_submission(self, **overrides) -> AssignmentSubmission:
        payload = {
            "status": "submitted",
            "submitted_at": datetime(2026, 1, 18, 9, 0, 0),
        }
        if "assignment_id" not in overrides:
            payload["assignment_id"] = self._create_assignment().id
        if "student_id" not in overrides:
            payload["student_id"] = self._create_student().id
        payload.update(overrides)
        submission = AssignmentSubmission(**payload)
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def _create_fee(self, **overrides) -> Fee:
        payload = {
            "amount": 2000.0,
            "paid_amount": 0.0,
            "due_date": date(2026, 1, 25),
        }
        if "student_id" not in overrides:
            payload["student_id"] = self._create_student().id
        payload.update(overrides)
        fee = Fee(**payload)
        self.db.add(fee)
        self.db.commit()
        self.db.refresh(fee)
        return fee

    def _create_attendance(self, **overrides) -> Attendance:
        payload = {
            "attendance_date": date(2026, 1, 10),
            "status": "present",
        }
        if "student_id" not in overrides:
            payload["student_id"] = self._create_student().id
        payload.update(overrides)
        attendance = Attendance(**payload)
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_successful_admin_dashboard_response(self):
        self.admin = self._create_admin()
        self._create_student(roll_number="ROLL-002", email="student2@example.com")
        self._create_teacher(user_id=self._create_user("teacher@example.com", "teacher").id)
        self._create_subject(name="Chemistry", code="CHEM-201")
        self._create_exam(name="Final", exam_date=date.today() + timedelta(days=60))
        self._create_assignment(title="Assignment 2")
        self._create_submission(status="submitted")
        self._create_fee(amount=500.0, paid_amount=500.0)
        self._create_attendance(status="present")
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("total_students", body)
        self.assertIn("total_teachers", body)
        self.assertIn("total_classes", body)
        self.assertIn("total_subjects", body)
        self.assertIn("total_exams", body)
        self.assertIn("total_assignments", body)
        self.assertIn("total_submissions", body)
        self.assertIn("total_fee_records", body)
        self.assertIn("paid_fee_records", body)
        self.assertIn("pending_fee_records", body)
        self.assertIn("total_attendance_records", body)
        self.assertIn("overall_attendance_percentage", body)
        self.assertIn("recent_students", body)
        self.assertIn("upcoming_exams", body)

    def test_unauthenticated_request(self):
        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 401, response.text)

    def test_authenticated_non_admin_request(self):
        teacher_user = self._create_user("teacher-dashboard@example.com", "teacher")
        self._create_teacher(user_id=teacher_user.id)
        self._login(teacher_user.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 403, response.text)
        self.assertEqual(response.json()["detail"], "Insufficient permissions")

    def test_correct_student_count(self):
        self.admin = self._create_admin()
        self._create_student(roll_number="ROLL-002", email="student2@example.com")
        self._create_student(roll_number="ROLL-003", email="student3@example.com")
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total_students"], 2)

    def test_correct_teacher_count(self):
        self.admin = self._create_admin()
        self._create_teacher(user_id=self._create_user("teacher1@example.com", "teacher").id)
        self._create_teacher(user_id=self._create_user("teacher2@example.com", "teacher").id)
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total_teachers"], 2)

    def test_correct_class_subject_exam_assignment_submission_counts(self):
        self.admin = self._create_admin()
        academic_class_1 = self._create_academic_class(name="CS Semester 4", code="CS-4", course="Computer Science", semester=4)
        self._create_academic_class(name="CS Semester 5", code="CS-5", course="Computer Science", semester=5)
        subject_1 = self._create_subject(name="Algorithms", code="ALGO-101")
        subject_2 = self._create_subject(name="Databases", code="DB-201")
        self._create_exam(name="Quiz", exam_date=date.today() + timedelta(days=10), academic_class_id=academic_class_1.id)
        self._create_exam(name="Practical", exam_date=date.today() + timedelta(days=20), academic_class_id=academic_class_1.id)
        assignment_1 = self._create_assignment(
            title="Assignment 1",
            subject_id=subject_1.id,
            academic_class_id=academic_class_1.id,
        )
        assignment_2 = self._create_assignment(
            title="Assignment 2",
            subject_id=subject_2.id,
            academic_class_id=academic_class_1.id,
        )
        student_1 = self._create_student(roll_number="ROLL-002", email="student2@example.com", academic_class_id=academic_class_1.id)
        student_2 = self._create_student(roll_number="ROLL-003", email="student3@example.com", academic_class_id=academic_class_1.id)
        self._create_submission(
            assignment_id=assignment_1.id,
            student_id=student_1.id,
            status="submitted",
        )
        self._create_submission(
            assignment_id=assignment_2.id,
            student_id=student_2.id,
            status="pending",
        )
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_classes"], 2)
        self.assertEqual(body["total_subjects"], 2)
        self.assertEqual(body["total_exams"], 2)
        self.assertEqual(body["total_assignments"], 2)
        self.assertEqual(body["total_submissions"], 2)

    def test_correct_fee_statistics(self):
        self.admin = self._create_admin()
        student_1 = self._create_student(roll_number="ROLL-002", email="student2@example.com")
        student_2 = self._create_student(roll_number="ROLL-003", email="student3@example.com")
        self._create_fee(student_id=student_1.id, amount=500.0, paid_amount=500.0)
        self._create_fee(student_id=student_2.id, amount=750.0, paid_amount=250.0)
        self._create_fee(student_id=student_1.id, amount=300.0, paid_amount=0.0)
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_fee_records"], 3)
        self.assertEqual(body["paid_fee_records"], 1)
        self.assertEqual(body["pending_fee_records"], 2)

    def test_correct_attendance_statistics(self):
        self.admin = self._create_admin()
        student = self._create_student(roll_number="ROLL-002", email="student2@example.com")
        self._create_attendance(student_id=student.id, attendance_date=date(2026, 1, 15), status="present")
        self._create_attendance(student_id=student.id, attendance_date=date(2026, 1, 16), status="present")
        self._create_attendance(student_id=student.id, attendance_date=date(2026, 1, 17), status="absent")
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_attendance_records"], 3)
        self.assertEqual(body["overall_attendance_percentage"], 66.67)

    def test_zero_database_behavior(self):
        self.admin = self._create_admin()
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_students"], 0)
        self.assertEqual(body["total_teachers"], 0)
        self.assertEqual(body["total_classes"], 0)
        self.assertEqual(body["total_subjects"], 0)
        self.assertEqual(body["total_exams"], 0)
        self.assertEqual(body["total_assignments"], 0)
        self.assertEqual(body["total_submissions"], 0)
        self.assertEqual(body["total_fee_records"], 0)
        self.assertEqual(body["paid_fee_records"], 0)
        self.assertEqual(body["pending_fee_records"], 0)
        self.assertEqual(body["total_attendance_records"], 0)
        self.assertEqual(body["overall_attendance_percentage"], 0.0)
        self.assertEqual(body["recent_students"], [])
        self.assertEqual(body["upcoming_exams"], [])

    def test_response_shape(self):
        self.admin = self._create_admin()
        student = self._create_student(roll_number="ROLL-002", email="student2@example.com")
        self._create_exam(name="Final Exam", exam_date=date.today() + timedelta(days=45))
        self._login(self.admin.email)

        response = self.client.get("/dashboard/admin")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body.keys()), {
            "total_students",
            "total_teachers",
            "total_classes",
            "total_subjects",
            "total_exams",
            "total_assignments",
            "total_submissions",
            "total_fee_records",
            "paid_fee_records",
            "pending_fee_records",
            "total_attendance_records",
            "overall_attendance_percentage",
            "recent_students",
            "upcoming_exams",
        })
        self.assertIsInstance(body["recent_students"], list)
        self.assertIsInstance(body["recent_students"][0]["id"], int)
        self.assertIn("created_at", body["recent_students"][0])
        self.assertIsInstance(body["upcoming_exams"], list)
        self.assertIn("academic_class_name", body["upcoming_exams"][0])
        self.assertEqual(body["recent_students"][0]["id"], student.id)
