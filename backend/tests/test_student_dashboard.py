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
    User,
)
from app.security import hash_password


class StudentDashboardApiTests(unittest.TestCase):
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

    def _create_user(self, email: str | None = None, role: str = "student") -> User:
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
            "exam_date": date.today() + timedelta(days=20),
        }
        if "academic_class_id" not in overrides:
            payload["academic_class_id"] = self._create_academic_class().id
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _create_student(self, user_id: int | None = None, **overrides) -> Student:
        if user_id is None:
            user = self._create_user(role="student")
            user_id = user.id

        payload = {
            "user_id": user_id,
            "name": "Alice Johnson",
            "roll_number": f"ROLL-{self._unique_suffix()}",
            "email": f"student-{self._unique_suffix()}@example.com",
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

    def _create_mark(self, **overrides) -> Mark:
        payload = {
            "marks": 80.0,
        }
        if "exam_id" not in overrides:
            payload["exam_id"] = self._create_exam().id
        if "student_id" not in overrides:
            payload["student_id"] = self._create_student().id
        if "subject_id" not in overrides:
            payload["subject_id"] = self._create_subject().id
        payload.update(overrides)
        mark = Mark(**payload)
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def _create_attendance(self, **overrides) -> Attendance:
        payload = {
            "attendance_date": date.today(),
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

    def _create_assignment(self, **overrides) -> Assignment:
        payload = {
            "title": "Assignment 1",
            "description": "Solve the questions",
            "due_date": date.today() + timedelta(days=15),
        }
        if "subject_id" not in overrides:
            payload["subject_id"] = self._create_subject().id
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
            "submitted_at": datetime.utcnow(),
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
            "amount": 500.0,
            "paid_amount": 0.0,
            "due_date": date.today() + timedelta(days=10),
        }
        if "student_id" not in overrides:
            payload["student_id"] = self._create_student().id
        payload.update(overrides)
        fee = Fee(**payload)
        self.db.add(fee)
        self.db.commit()
        self.db.refresh(fee)
        return fee

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_successful_student_dashboard_response(self):
        student_user = self._create_user(email=f"student-success-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(
            name="CS Semester 4",
            code=f"CS-{self._unique_suffix()}",
            course="Computer Science",
            semester=4,
        )
        subject = self._create_subject(name="Algebra", code=f"ALG-{self._unique_suffix()}")
        exam = self._create_exam(
            name="Quiz 1",
            exam_type="quiz",
            exam_date=date.today() + timedelta(days=7),
            academic_class_id=academic_class.id,
        )
        student = self._create_student(
            user_id=student_user.id,
            name="Alice Johnson",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"alice-{self._unique_suffix()}@example.com",
            phone="5551111111",
            course="Computer Science",
            semester=4,
            academic_class_id=academic_class.id,
        )
        self._create_mark(student_id=student.id, exam_id=exam.id, subject_id=subject.id, marks=88.0)
        self._create_attendance(student_id=student.id, attendance_date=date.today(), status="present")
        assignment = self._create_assignment(
            title="Homework 1",
            subject_id=subject.id,
            academic_class_id=academic_class.id,
            due_date=date.today() + timedelta(days=5),
        )
        self._create_submission(assignment_id=assignment.id, student_id=student.id, status="submitted")
        self._create_fee(student_id=student.id, amount=400.0, paid_amount=200.0)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student.id)
        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["total_results"], 1)
        self.assertEqual(body["overall_grade"], "A")

    def test_unauthenticated_request(self):
        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 401, response.text)

    def test_authenticated_non_student_request(self):
        admin_user = self._create_user(email=f"admin-{self._unique_suffix()}@example.com", role="admin")
        self._login(admin_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 403, response.text)
        self.assertEqual(response.json()["detail"], "Insufficient permissions")

    def test_correct_student_information(self):
        student_user = self._create_user(email=f"student-info-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 5", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=5)
        student = self._create_student(
            user_id=student_user.id,
            name="Bob Smith",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"bob-{self._unique_suffix()}@example.com",
            phone="5552222222",
            course="Computer Science",
            semester=5,
            academic_class_id=academic_class.id,
        )
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student.id)
        self.assertEqual(body["student"]["name"], "Bob Smith")
        self.assertEqual(body["student"]["roll_number"], student.roll_number)
        self.assertEqual(body["student"]["email"], student.email)
        self.assertEqual(body["student"]["phone"], "5552222222")
        self.assertEqual(body["student"]["course"], "Computer Science")
        self.assertEqual(body["student"]["semester"], 5)

    def test_correct_academic_class_information(self):
        student_user = self._create_user(email=f"student-class-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(
            name="CS Semester 6",
            code=f"CS-{self._unique_suffix()}",
            course="Computer Science",
            semester=6,
        )
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Charlie Brown",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"charlie-{self._unique_suffix()}@example.com",
            phone="5553333333",
            course="Computer Science",
            semester=6,
        )
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIsNotNone(body["academic_class"])
        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["academic_class"]["name"], academic_class.name)
        self.assertEqual(body["academic_class"]["code"], academic_class.code)
        self.assertEqual(body["academic_class"]["course"], academic_class.course)
        self.assertEqual(body["academic_class"]["semester"], academic_class.semester)
        self.assertEqual(body["student"]["id"], student.id)

    def test_correct_marks_statistics(self):
        student_user = self._create_user(email=f"student-marks-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 7", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=7)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Dana White",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"dana-{self._unique_suffix()}@example.com",
            phone="5554444444",
            course="Computer Science",
            semester=7,
        )
        subject_a = self._create_subject(name="Algebra", code=f"ALG-{self._unique_suffix()}")
        subject_b = self._create_subject(name="Biology", code=f"BIO-{self._unique_suffix()}")
        exam_a = self._create_exam(name="Quiz 1", exam_type="quiz", exam_date=date.today() + timedelta(days=5), academic_class_id=academic_class.id)
        exam_b = self._create_exam(name="Quiz 2", exam_type="quiz", exam_date=date.today() + timedelta(days=15), academic_class_id=academic_class.id)
        self._create_mark(student_id=student.id, exam_id=exam_a.id, subject_id=subject_a.id, marks=80.0)
        self._create_mark(student_id=student.id, exam_id=exam_b.id, subject_id=subject_b.id, marks=90.0)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_results"], 2)
        self.assertEqual(body["total_possible_marks"], 200)
        self.assertEqual(body["marks_obtained"], 170.0)
        self.assertEqual(body["percentage"], 85.0)
        self.assertEqual(body["average_marks"], 85.0)
        self.assertEqual(body["overall_grade"], "A")
        self.assertEqual(len(body["recent_marks"]), 2)

    def test_correct_grade_calculation(self):
        student_user = self._create_user(email=f"student-grade-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 8", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=8)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Emma Stone",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"emma-{self._unique_suffix()}@example.com",
            phone="5555555555",
            course="Computer Science",
            semester=8,
        )
        subject = self._create_subject(name="Chemistry", code=f"CHEM-{self._unique_suffix()}")
        exam = self._create_exam(name="Final", exam_type="final", exam_date=date.today() + timedelta(days=30), academic_class_id=academic_class.id)
        self._create_mark(student_id=student.id, exam_id=exam.id, subject_id=subject.id, marks=95.0)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["overall_grade"], "A+")
        self.assertEqual(body["recent_marks"][0]["grade"], "A+")

    def test_correct_attendance_statistics(self):
        student_user = self._create_user(email=f"student-attendance-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 9", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=9)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Frank Blue",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"frank-{self._unique_suffix()}@example.com",
            phone="5556666666",
            course="Computer Science",
            semester=9,
        )
        self._create_attendance(student_id=student.id, attendance_date=date.today() - timedelta(days=2), status="present")
        self._create_attendance(student_id=student.id, attendance_date=date.today() - timedelta(days=1), status="present")
        self._create_attendance(student_id=student.id, attendance_date=date.today(), status="absent")
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_attendance_records"], 3)
        self.assertEqual(body["present_attendance_records"], 2)
        self.assertEqual(body["absent_attendance_records"], 1)
        self.assertEqual(body["attendance_percentage"], 66.67)

    def test_correct_exam_statistics(self):
        student_user = self._create_user(email=f"student-exams-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 10", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=10)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Grace Hall",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"grace-{self._unique_suffix()}@example.com",
            phone="5557777777",
            course="Computer Science",
            semester=10,
        )
        self._create_exam(name="Past Quiz", exam_type="quiz", exam_date=date.today() - timedelta(days=5), academic_class_id=academic_class.id)
        self._create_exam(name="Upcoming Quiz", exam_type="quiz", exam_date=date.today() + timedelta(days=5), academic_class_id=academic_class.id)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_exams"], 2)
        self.assertEqual(body["past_exams_count"], 1)
        self.assertEqual(len(body["upcoming_exams"]), 1)
        self.assertEqual(body["upcoming_exams"][0]["name"], "Upcoming Quiz")

    def test_correct_assignment_statistics(self):
        student_user = self._create_user(email=f"student-assignments-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 11", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=11)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Henry Pond",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"henry-{self._unique_suffix()}@example.com",
            phone="5558888888",
            course="Computer Science",
            semester=11,
        )
        subject = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}")
        assignment_1 = self._create_assignment(title="Assignment A", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=7))
        assignment_2 = self._create_assignment(title="Assignment B", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=14))
        assignment_3 = self._create_assignment(title="Assignment C", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=21))
        other_class = self._create_academic_class(name="Math Semester 1", code=f"MATH-{self._unique_suffix()}", course="Mathematics", semester=1)
        self._create_assignment(title="Other Assignment", subject_id=subject.id, academic_class_id=other_class.id, due_date=date.today() + timedelta(days=30))
        self._create_submission(assignment_id=assignment_1.id, student_id=student.id, status="submitted")
        self._create_submission(assignment_id=assignment_2.id, student_id=student.id, status="late")
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_assignments"], 3)
        self.assertEqual(body["submitted_assignments"], 2)
        self.assertEqual(body["pending_assignments"], 1)

    def test_correct_submission_statistics(self):
        student_user = self._create_user(email=f"student-submissions-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 12", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=12)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Iris Gray",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"iris-{self._unique_suffix()}@example.com",
            phone="5559999999",
            course="Computer Science",
            semester=12,
        )
        subject = self._create_subject(name="Literature", code=f"LIT-{self._unique_suffix()}")
        assignment_1 = self._create_assignment(title="Essay 1", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=3))
        assignment_2 = self._create_assignment(title="Essay 2", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=10))
        self._create_submission(assignment_id=assignment_1.id, student_id=student.id, status="submitted")
        self._create_submission(assignment_id=assignment_2.id, student_id=student.id, status="pending")
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["submitted_assignments"], 1)
        self.assertEqual(body["pending_assignments"], 1)
        self.assertEqual(body["total_assignments"], 2)

    def test_correct_fee_statistics(self):
        student_user = self._create_user(email=f"student-fees-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 13", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=13)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Jack Green",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"jack-{self._unique_suffix()}@example.com",
            phone="5551010101",
            course="Computer Science",
            semester=13,
        )
        self._create_fee(student_id=student.id, amount=500.0, paid_amount=500.0)
        self._create_fee(student_id=student.id, amount=300.0, paid_amount=100.0)
        self._create_fee(student_id=student.id, amount=200.0, paid_amount=0.0)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total_fee_records"], 3)
        self.assertEqual(body["paid_fee_records"], 1)
        self.assertEqual(body["pending_fee_records"], 2)
        self.assertEqual(body["total_fee_amount"], 1000.0)
        self.assertEqual(body["paid_fee_amount"], 600.0)
        self.assertEqual(body["due_fee_amount"], 400.0)

    def test_zero_data_behavior(self):
        student_user = self._create_user(email=f"student-zero-{self._unique_suffix()}@example.com", role="student")
        student = self._create_student(
            user_id=student_user.id,
            name="Kelly Black",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"kelly-{self._unique_suffix()}@example.com",
            phone="5552020202",
            course="Computer Science",
            semester=1,
            academic_class_id=None,
        )
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student.id)
        self.assertIsNone(body["academic_class"])
        self.assertEqual(body["total_results"], 0)
        self.assertEqual(body["total_possible_marks"], 0)
        self.assertEqual(body["marks_obtained"], 0.0)
        self.assertEqual(body["percentage"], 0.0)
        self.assertEqual(body["average_marks"], 0.0)
        self.assertEqual(body["overall_grade"], "F")
        self.assertEqual(body["recent_marks"], [])
        self.assertEqual(body["total_attendance_records"], 0)
        self.assertEqual(body["present_attendance_records"], 0)
        self.assertEqual(body["absent_attendance_records"], 0)
        self.assertEqual(body["attendance_percentage"], 0.0)
        self.assertEqual(body["total_exams"], 0)
        self.assertEqual(body["upcoming_exams"], [])
        self.assertEqual(body["past_exams_count"], 0)
        self.assertEqual(body["total_assignments"], 0)
        self.assertEqual(body["submitted_assignments"], 0)
        self.assertEqual(body["pending_assignments"], 0)
        self.assertEqual(body["total_fee_records"], 0)
        self.assertEqual(body["paid_fee_records"], 0)
        self.assertEqual(body["pending_fee_records"], 0)
        self.assertEqual(body["total_fee_amount"], 0.0)
        self.assertEqual(body["paid_fee_amount"], 0.0)
        self.assertEqual(body["due_fee_amount"], 0.0)

    def test_response_shape(self):
        student_user = self._create_user(email=f"student-shape-{self._unique_suffix()}@example.com", role="student")
        academic_class = self._create_academic_class(name="CS Semester 14", code=f"CS-{self._unique_suffix()}", course="Computer Science", semester=14)
        student = self._create_student(
            user_id=student_user.id,
            academic_class_id=academic_class.id,
            name="Laura King",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"laura-{self._unique_suffix()}@example.com",
            phone="5553030303",
            course="Computer Science",
            semester=14,
        )
        subject = self._create_subject(name="Statistics", code=f"STAT-{self._unique_suffix()}")
        exam = self._create_exam(name="Midterm", exam_type="midterm", exam_date=date.today() + timedelta(days=12), academic_class_id=academic_class.id)
        self._create_mark(student_id=student.id, exam_id=exam.id, subject_id=subject.id, marks=90.0)
        self._create_attendance(student_id=student.id, attendance_date=date.today(), status="present")
        assignment = self._create_assignment(title="Project", subject_id=subject.id, academic_class_id=academic_class.id, due_date=date.today() + timedelta(days=8))
        self._create_submission(assignment_id=assignment.id, student_id=student.id, status="submitted")
        self._create_fee(student_id=student.id, amount=1000.0, paid_amount=500.0)
        self._login(student_user.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        expected_keys = {
            "student",
            "academic_class",
            "total_results",
            "total_possible_marks",
            "marks_obtained",
            "percentage",
            "average_marks",
            "overall_grade",
            "recent_marks",
            "total_attendance_records",
            "present_attendance_records",
            "absent_attendance_records",
            "attendance_percentage",
            "total_exams",
            "upcoming_exams",
            "past_exams_count",
            "total_assignments",
            "submitted_assignments",
            "pending_assignments",
            "total_fee_records",
            "paid_fee_records",
            "pending_fee_records",
            "total_fee_amount",
            "paid_fee_amount",
            "due_fee_amount",
        }
        self.assertEqual(set(body.keys()), expected_keys)
        self.assertIsInstance(body["student"], dict)
        self.assertIsInstance(body["academic_class"], dict)
        self.assertIsInstance(body["recent_marks"], list)
        self.assertIsInstance(body["upcoming_exams"], list)
        self.assertEqual(body["student"]["id"], student.id)

    def test_student_isolation(self):
        student_user_a = self._create_user(email=f"student-a-{self._unique_suffix()}@example.com", role="student")
        student_user_b = self._create_user(email=f"student-b-{self._unique_suffix()}@example.com", role="student")

        class_a = self._create_academic_class(name="Science A", code=f"SCI-{self._unique_suffix()}", course="Science", semester=1)
        class_b = self._create_academic_class(name="Science B", code=f"SCI-{self._unique_suffix()}", course="Science", semester=2)

        subject_a = self._create_subject(name="Algebra", code=f"ALG-{self._unique_suffix()}")
        subject_b = self._create_subject(name="Biology", code=f"BIO-{self._unique_suffix()}")

        student_a = self._create_student(
            user_id=student_user_a.id,
            academic_class_id=class_a.id,
            name="Student A",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"student-a-{self._unique_suffix()}@example.com",
            phone="5550000001",
            course="Science",
            semester=1,
        )
        student_b = self._create_student(
            user_id=student_user_b.id,
            academic_class_id=class_b.id,
            name="Student B",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"student-b-{self._unique_suffix()}@example.com",
            phone="5550000002",
            course="Science",
            semester=2,
        )

        exam_a = self._create_exam(name="A Exam", exam_type="midterm", exam_date=date.today() + timedelta(days=10), academic_class_id=class_a.id)
        exam_b = self._create_exam(name="B Exam", exam_type="midterm", exam_date=date.today() + timedelta(days=15), academic_class_id=class_b.id)

        self._create_mark(student_id=student_a.id, exam_id=exam_a.id, subject_id=subject_a.id, marks=90.0)
        self._create_mark(student_id=student_b.id, exam_id=exam_b.id, subject_id=subject_b.id, marks=40.0)

        self._create_attendance(student_id=student_a.id, attendance_date=date.today(), status="present")
        self._create_attendance(student_id=student_b.id, attendance_date=date.today(), status="absent")

        assignment_a = self._create_assignment(title="A Assignment", subject_id=subject_a.id, academic_class_id=class_a.id, due_date=date.today() + timedelta(days=5))
        assignment_b = self._create_assignment(title="B Assignment", subject_id=subject_b.id, academic_class_id=class_b.id, due_date=date.today() + timedelta(days=6))

        self._create_submission(assignment_id=assignment_a.id, student_id=student_a.id, status="submitted")
        self._create_submission(assignment_id=assignment_b.id, student_id=student_b.id, status="pending")

        self._create_fee(student_id=student_a.id, amount=600.0, paid_amount=600.0)
        self._create_fee(student_id=student_b.id, amount=900.0, paid_amount=100.0)

        self._login(student_user_a.email)

        response = self.client.get("/dashboard/student")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student_a.id)
        self.assertEqual(body["academic_class"]["id"], class_a.id)
        self.assertNotEqual(body["academic_class"]["id"], class_b.id)
        self.assertEqual(body["total_results"], 1)
        self.assertEqual(body["marks_obtained"], 90.0)
        self.assertEqual(body["total_attendance_records"], 1)
        self.assertEqual(body["present_attendance_records"], 1)
        self.assertEqual(body["absent_attendance_records"], 0)
        self.assertEqual(body["total_assignments"], 1)
        self.assertEqual(body["submitted_assignments"], 1)
        self.assertEqual(body["pending_assignments"], 0)
        self.assertEqual(body["total_fee_records"], 1)
        self.assertEqual(body["paid_fee_records"], 1)
        self.assertEqual(body["pending_fee_records"], 0)
        self.assertNotIn("Biology", [item["subject_name"] for item in body["recent_marks"]])
        self.assertNotEqual(body["student"]["name"], "Student B")
