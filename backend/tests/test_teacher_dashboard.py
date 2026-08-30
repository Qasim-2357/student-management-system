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
    Student,
    Subject,
    Teacher,
    User,
)
from app.security import hash_password


class TeacherDashboardApiTests(unittest.TestCase):
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

    def _assign_class_to_teacher(self, teacher: Teacher, academic_class: AcademicClass) -> None:
        teacher.academic_classes.append(academic_class)
        self.db.commit()

    def _assign_subject_to_teacher(self, teacher: Teacher, subject: Subject) -> None:
        teacher.subjects.append(subject)
        self.db.commit()

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def _build_teacher_with_class_and_subject(self):
        """Create a teacher assigned to one academic class and one subject."""
        teacher = self._create_teacher()
        academic_class = self._create_academic_class()
        subject = self._create_subject()
        self._assign_class_to_teacher(teacher, academic_class)
        self._assign_subject_to_teacher(teacher, subject)
        return teacher, academic_class, subject

    # 1. Successful teacher dashboard response
    def test_successful_teacher_dashboard_response(self):
        teacher, academic_class, subject = self._build_teacher_with_class_and_subject()
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")

        self.assertEqual(response.status_code, 200, response.text)

    # 2. Unauthenticated request -> 401
    def test_unauthenticated_request(self):
        response = self.client.get("/dashboard/teacher")

        self.assertEqual(response.status_code, 401, response.text)

    # 3. Authenticated non-teacher -> 403
    def test_authenticated_non_teacher_request(self):
        admin_user = self._create_user(role="admin")
        self._login(admin_user.email)

        response = self.client.get("/dashboard/teacher")

        self.assertEqual(response.status_code, 403, response.text)
        self.assertEqual(response.json()["detail"], "Insufficient permissions")

    # 4 & 6. Correct class count and teacher-specific counts
    def test_correct_class_count(self):
        teacher = self._create_teacher()
        class_1 = self._create_academic_class(code=f"C1-{self._unique_suffix()}")
        class_2 = self._create_academic_class(code=f"C2-{self._unique_suffix()}")
        self._assign_class_to_teacher(teacher, class_1)
        self._assign_class_to_teacher(teacher, class_2)
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_assigned_classes"], 2)
        self.assertEqual(len(body["assigned_classes"]), 2)

    # 5. Correct student count
    def test_correct_student_count(self):
        teacher, academic_class, _subject = self._build_teacher_with_class_and_subject()
        self._create_student(academic_class_id=academic_class.id)
        self._create_student(academic_class_id=academic_class.id)
        other_class = self._create_academic_class()
        self._create_student(academic_class_id=other_class.id)
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_students"], 2)

    # 7. Correct subject count
    def test_correct_subject_count(self):
        teacher = self._create_teacher()
        subject_1 = self._create_subject(name="Physics")
        subject_2 = self._create_subject(name="Chemistry")
        self._assign_subject_to_teacher(teacher, subject_1)
        self._assign_subject_to_teacher(teacher, subject_2)
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_assigned_subjects"], 2)
        self.assertEqual(len(body["assigned_subjects"]), 2)

    # 8. Relevant exam statistics
    def test_relevant_exam_statistics(self):
        teacher, academic_class, _subject = self._build_teacher_with_class_and_subject()
        self._create_exam(
            name="Class Quiz",
            academic_class_id=academic_class.id,
            exam_date=date.today() + timedelta(days=5),
        )
        past_exam_class = academic_class
        self._create_exam(
            name="Old Exam",
            academic_class_id=past_exam_class.id,
            exam_date=date.today() - timedelta(days=5),
        )
        other_class = self._create_academic_class()
        self._create_exam(name="Unrelated Exam", academic_class_id=other_class.id)
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_relevant_exams"], 2)
        self.assertEqual(len(body["upcoming_exams"]), 1)
        self.assertEqual(body["upcoming_exams"][0]["name"], "Class Quiz")

    # 9. Assignment/submission statistics
    def test_assignment_and_submission_statistics(self):
        teacher, academic_class, subject = self._build_teacher_with_class_and_subject()
        assignment = self._create_assignment(
            subject_id=subject.id,
            academic_class_id=academic_class.id,
        )
        student_1 = self._create_student(academic_class_id=academic_class.id)
        student_2 = self._create_student(academic_class_id=academic_class.id)
        self._create_submission(
            assignment_id=assignment.id,
            student_id=student_1.id,
            status="submitted",
        )
        self._create_submission(
            assignment_id=assignment.id,
            student_id=student_2.id,
            status="pending",
        )

        # An assignment for a class/subject NOT assigned to this teacher
        # must not be counted.
        other_subject = self._create_subject()
        other_class = self._create_academic_class()
        unrelated_assignment = self._create_assignment(
            subject_id=other_subject.id,
            academic_class_id=other_class.id,
        )
        self._create_submission(assignment_id=unrelated_assignment.id)

        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_assignments"], 1)
        self.assertEqual(body["total_submissions"], 2)
        self.assertEqual(body["submitted_submissions"], 1)
        self.assertEqual(body["pending_submissions"], 1)

    def test_attendance_statistics(self):
        teacher, academic_class, _subject = self._build_teacher_with_class_and_subject()
        student = self._create_student(academic_class_id=academic_class.id)
        self._create_attendance(
            student_id=student.id,
            attendance_date=date(2026, 1, 15),
            status="present",
        )
        self._create_attendance(
            student_id=student.id,
            attendance_date=date(2026, 1, 16),
            status="present",
        )
        self._create_attendance(
            student_id=student.id,
            attendance_date=date(2026, 1, 17),
            status="absent",
        )

        # Attendance for a student outside the teacher's classes must not
        # be counted.
        other_class = self._create_academic_class()
        other_student = self._create_student(academic_class_id=other_class.id)
        self._create_attendance(
            student_id=other_student.id,
            attendance_date=date(2026, 1, 15),
            status="present",
        )

        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_attendance_records"], 3)
        self.assertEqual(body["present_attendance_records"], 2)
        self.assertEqual(body["overall_attendance_percentage"], 66.67)

    # 10. Empty/zero-data behavior
    def test_zero_data_behavior(self):
        teacher = self._create_teacher()
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(body["total_assigned_classes"], 0)
        self.assertEqual(body["total_assigned_subjects"], 0)
        self.assertEqual(body["total_students"], 0)
        self.assertEqual(body["total_relevant_exams"], 0)
        self.assertEqual(body["upcoming_exams"], [])
        self.assertEqual(body["total_assignments"], 0)
        self.assertEqual(body["total_submissions"], 0)
        self.assertEqual(body["submitted_submissions"], 0)
        self.assertEqual(body["pending_submissions"], 0)
        self.assertEqual(body["total_attendance_records"], 0)
        self.assertEqual(body["present_attendance_records"], 0)
        self.assertEqual(body["overall_attendance_percentage"], 0.0)
        self.assertEqual(body["assigned_classes"], [])
        self.assertEqual(body["assigned_subjects"], [])

    # 11. Response shape
    def test_response_shape(self):
        teacher, academic_class, subject = self._build_teacher_with_class_and_subject()
        self._login(teacher.user.email)

        response = self.client.get("/dashboard/teacher")
        body = response.json()

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            set(body.keys()),
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
        self.assertEqual(
            set(body["teacher"].keys()), {"id", "name", "email", "phone"}
        )
        self.assertEqual(body["teacher"]["id"], teacher.id)
        self.assertIsInstance(body["assigned_classes"], list)
        self.assertIsInstance(body["assigned_subjects"], list)
        self.assertIn("student_count", body["assigned_classes"][0])
        self.assertIn("code", body["assigned_subjects"][0])

    # 12. Teacher isolation
    def test_teacher_isolation(self):
        teacher_a, class_a, subject_a = self._build_teacher_with_class_and_subject()
        teacher_b, class_b, subject_b = self._build_teacher_with_class_and_subject()

        student_a1 = self._create_student(academic_class_id=class_a.id)
        student_a2 = self._create_student(academic_class_id=class_a.id)
        self._create_student(academic_class_id=class_b.id)

        assignment_a = self._create_assignment(
            subject_id=subject_a.id, academic_class_id=class_a.id
        )
        self._create_submission(
            assignment_id=assignment_a.id, student_id=student_a1.id, status="submitted"
        )
        self._create_submission(
            assignment_id=assignment_a.id, student_id=student_a2.id, status="pending"
        )

        assignment_b = self._create_assignment(
            subject_id=subject_b.id, academic_class_id=class_b.id
        )
        self._create_submission(assignment_id=assignment_b.id, status="submitted")
        self._create_submission(assignment_id=assignment_b.id, status="submitted")
        self._create_submission(assignment_id=assignment_b.id, status="submitted")

        self._create_exam(name="Class A Exam", academic_class_id=class_a.id)
        self._create_exam(name="Class B Exam 1", academic_class_id=class_b.id)
        self._create_exam(name="Class B Exam 2", academic_class_id=class_b.id)

        self._login(teacher_a.user.email)
        response_a = self.client.get("/dashboard/teacher")
        self.assertEqual(response_a.status_code, 200, response_a.text)
        body_a = response_a.json()

        self.client.post("/auth/logout")
        self._login(teacher_b.user.email)
        response_b = self.client.get("/dashboard/teacher")
        self.assertEqual(response_b.status_code, 200, response_b.text)
        body_b = response_b.json()

        self.assertEqual(body_a["teacher"]["id"], teacher_a.id)
        self.assertEqual(body_b["teacher"]["id"], teacher_b.id)

        self.assertEqual(body_a["total_students"], 2)
        self.assertEqual(body_b["total_students"], 1)

        self.assertEqual(body_a["total_submissions"], 2)
        self.assertEqual(body_b["total_submissions"], 3)

        self.assertEqual(body_a["total_relevant_exams"], 1)
        self.assertEqual(body_b["total_relevant_exams"], 2)

        self.assertNotEqual(body_a["teacher"]["id"], body_b["teacher"]["id"])


if __name__ == "__main__":
    unittest.main()