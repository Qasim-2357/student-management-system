import unittest
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Exam, Mark, Student, Subject, User
from app.security import hash_password
from app.services.grades import calculate_grade


class MarksheetApiTests(unittest.TestCase):
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

    def _create_student(self, user_id: int | None = None, **overrides) -> Student:
        if user_id is None:
            user = self._create_user(f"student-{self._unique_suffix()}@example.com", "student")
            user_id = user.id

        payload = {
            "user_id": user_id,
            "name": "Alice Johnson",
            "roll_number": f"ROLL-{self._unique_suffix()}",
            "email": f"student-{self._unique_suffix()}@example.com",
            "phone": "5551234567",
            "date_of_birth": date(2002, 5, 4),
            "course": "Computer Science",
            "semester": 3,
        }
        payload.update(overrides)
        student = Student(**payload)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def _create_exam(self, academic_class_id: int, **overrides) -> Exam:
        payload = {
            "name": "Midterm",
            "exam_type": "midterm",
            "exam_date": date(2026, 1, 15),
            "academic_class_id": academic_class_id,
        }
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def _create_mark(
        self,
        *,
        exam_id: int,
        student_id: int,
        subject_id: int,
        marks: float,
    ) -> Mark:
        mark = Mark(
            exam_id=exam_id,
            student_id=student_id,
            subject_id=subject_id,
            marks=marks,
        )
        self.db.add(mark)
        self.db.commit()
        self.db.refresh(mark)
        return mark

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_marksheet_response(self):
        academic_class = self._create_academic_class(name="CS Semester 4", code=f"CS-{self._unique_suffix()}")
        student = self._create_student(
            academic_class_id=academic_class.id,
            name="Alice Johnson",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"alice-{self._unique_suffix()}@example.com",
        )
        math = self._create_subject(name="Mathematics", code=f"MATH-{self._unique_suffix()}")
        physics = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}")
        exam_1 = self._create_exam(academic_class_id=academic_class.id, name="Midterm", exam_type="midterm")
        exam_2 = self._create_exam(academic_class_id=academic_class.id, name="Final", exam_type="final")
        self._create_mark(exam_id=exam_1.id, student_id=student.id, subject_id=math.id, marks=85.0)
        self._create_mark(exam_id=exam_2.id, student_id=student.id, subject_id=physics.id, marks=90.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["student"]["id"], student.id)
        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(len(body["exam_marks"]), 2)
        self.assertEqual(body["overall"]["total_marks_obtained"], 175.0)

    def test_marksheet_requires_authentication(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 401, response.text)

    def test_marksheet_missing_student_returns_404(self):
        self._login(self.admin.email)

        response = self.client.get("/students/9999/marksheet")

        self.assertEqual(response.status_code, 404, response.text)

    def test_marksheet_contains_student_information(self):
        academic_class = self._create_academic_class()
        student = self._create_student(
            academic_class_id=academic_class.id,
            name="Bob Smith",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"bob-{self._unique_suffix()}@example.com",
            phone="5551112222",
            date_of_birth=date(2001, 2, 3),
            course="Mathematics",
            semester=4,
        )
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()["student"]
        self.assertEqual(body["id"], student.id)
        self.assertEqual(body["name"], "Bob Smith")
        self.assertEqual(body["roll_number"], student.roll_number)
        self.assertEqual(body["email"], student.email)
        self.assertEqual(body["phone"], "5551112222")
        self.assertEqual(body["date_of_birth"], "2001-02-03")
        self.assertEqual(body["course"], "Mathematics")
        self.assertEqual(body["semester"], 4)

    def test_marksheet_contains_class_information(self):
        academic_class = self._create_academic_class(
            name="Math Semester 2",
            code=f"MATH-{self._unique_suffix()}",
            course="Mathematics",
            semester=2,
        )
        student = self._create_student(academic_class_id=academic_class.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        class_payload = response.json()["academic_class"]
        self.assertEqual(class_payload["name"], "Math Semester 2")
        self.assertEqual(class_payload["code"], academic_class.code)
        self.assertEqual(class_payload["course"], "Mathematics")
        self.assertEqual(class_payload["semester"], 2)

    def test_marksheet_groups_marks_by_exam(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        math = self._create_subject(name="Mathematics", code=f"MATH-{self._unique_suffix()}")
        physics = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}")
        exam_1 = self._create_exam(academic_class_id=academic_class.id, name="Quiz 1", exam_type="quiz")
        exam_2 = self._create_exam(academic_class_id=academic_class.id, name="Quiz 2", exam_type="quiz")
        self._create_mark(exam_id=exam_1.id, student_id=student.id, subject_id=math.id, marks=80.0)
        self._create_mark(exam_id=exam_1.id, student_id=student.id, subject_id=physics.id, marks=70.0)
        self._create_mark(exam_id=exam_2.id, student_id=student.id, subject_id=math.id, marks=90.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(len(body["exam_marks"]), 2)
        self.assertEqual(body["exam_marks"][0]["exam_name"], "Quiz 1")
        self.assertEqual(len(body["exam_marks"][0]["subjects"]), 2)
        self.assertEqual(body["exam_marks"][1]["exam_name"], "Quiz 2")

    def test_marksheet_contains_exam_information(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject(name="Chemistry", code=f"CHEM-{self._unique_suffix()}")
        exam = self._create_exam(
            academic_class_id=academic_class.id,
            name="Unit Test",
            exam_type="unit",
            exam_date=date(2026, 3, 10),
        )
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=subject.id, marks=88.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        exam_payload = response.json()["exam_marks"][0]
        self.assertEqual(exam_payload["exam_id"], exam.id)
        self.assertEqual(exam_payload["exam_name"], "Unit Test")
        self.assertEqual(exam_payload["exam_type"], "unit")
        self.assertEqual(exam_payload["exam_date"], "2026-03-10")

    def test_marksheet_contains_subject_information(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject(name="Biology", code=f"BIO-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=subject.id, marks=76.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        subject_payload = response.json()["exam_marks"][0]["subjects"][0]
        self.assertEqual(subject_payload["subject_id"], subject.id)
        self.assertEqual(subject_payload["subject_name"], "Biology")
        self.assertEqual(subject_payload["subject_code"], subject.code)
        self.assertEqual(subject_payload["marks_obtained"], 76.0)

    def test_marksheet_uses_grade_calculation_for_each_subject(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject(name="Algebra", code=f"ALG-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=subject.id, marks=88.5)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["exam_marks"][0]["subjects"][0]["grade"], calculate_grade(88.5))

    def test_marksheet_reports_total_marks(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        math = self._create_subject(name="Mathematics", code=f"MATH-{self._unique_suffix()}")
        physics = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=math.id, marks=82.0)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=physics.id, marks=68.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        overall = response.json()["overall"]
        self.assertEqual(overall["total_marks_obtained"], 150.0)
        self.assertEqual(overall["total_possible_marks"], 200)

    def test_marksheet_calculates_percentage(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        math = self._create_subject(name="Mathematics", code=f"MATH-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=math.id, marks=75.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["overall"]["percentage"], 75.0)

    def test_marksheet_calculates_overall_grade(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        math = self._create_subject(name="Mathematics", code=f"MATH-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=math.id, marks=92.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["overall"]["overall_grade"], "A+")

    def test_marksheet_returns_zero_safe_values_when_student_has_no_marks(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["exam_marks"], [])
        self.assertEqual(body["overall"]["total_marks_obtained"], 0.0)
        self.assertEqual(body["overall"]["total_possible_marks"], 0)
        self.assertEqual(body["overall"]["percentage"], 0.0)
        self.assertEqual(body["overall"]["overall_grade"], "F")

    def test_marksheet_has_deterministic_ordering(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject_1 = self._create_subject(name="Chemistry", code=f"CHEM-{self._unique_suffix()}")
        subject_2 = self._create_subject(name="Physics", code=f"PHYS-{self._unique_suffix()}")
        exam_1 = self._create_exam(academic_class_id=academic_class.id, name="Midterm", exam_type="midterm")
        exam_2 = self._create_exam(academic_class_id=academic_class.id, name="Final", exam_type="final")
        self._create_mark(exam_id=exam_2.id, student_id=student.id, subject_id=subject_2.id, marks=60.0)
        self._create_mark(exam_id=exam_1.id, student_id=student.id, subject_id=subject_1.id, marks=70.0)
        self._create_mark(exam_id=exam_1.id, student_id=student.id, subject_id=subject_2.id, marks=80.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual([item["exam_id"] for item in body["exam_marks"]], [exam_1.id, exam_2.id])
        self.assertEqual(
            [item["subject_id"] for item in body["exam_marks"][0]["subjects"]],
            [subject_1.id, subject_2.id],
        )

    def test_marksheet_response_shape(self):
        academic_class = self._create_academic_class()
        student = self._create_student(academic_class_id=academic_class.id)
        subject = self._create_subject(name="English", code=f"ENG-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student.id, subject_id=subject.id, marks=81.0)
        self._login(self.admin.email)

        response = self.client.get(f"/students/{student.id}/marksheet")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body.keys()), {"student", "academic_class", "exam_marks", "overall"})
        self.assertEqual(
            set(body["student"].keys()),
            {"id", "name", "roll_number", "email", "phone", "date_of_birth", "course", "semester"},
        )
        self.assertEqual(
            set(body["overall"].keys()),
            {"total_marks_obtained", "total_possible_marks", "percentage", "overall_grade"},
        )
        self.assertEqual(
            set(body["exam_marks"][0]["subjects"][0].keys()),
            {"subject_id", "subject_name", "subject_code", "marks_obtained", "grade"},
        )

    def test_marksheet_is_student_specific(self):
        academic_class = self._create_academic_class()
        student_a = self._create_student(
            academic_class_id=academic_class.id,
            name="Student A",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"student-a-{self._unique_suffix()}@example.com",
        )
        student_b = self._create_student(
            academic_class_id=academic_class.id,
            name="Student B",
            roll_number=f"ROLL-{self._unique_suffix()}",
            email=f"student-b-{self._unique_suffix()}@example.com",
        )
        subject = self._create_subject(name="History", code=f"HIST-{self._unique_suffix()}")
        exam = self._create_exam(academic_class_id=academic_class.id)
        self._create_mark(exam_id=exam.id, student_id=student_a.id, subject_id=subject.id, marks=92.0)
        self._create_mark(exam_id=exam.id, student_id=student_b.id, subject_id=subject.id, marks=60.0)
        self._login(self.admin.email)

        response_a = self.client.get(f"/students/{student_a.id}/marksheet")
        response_b = self.client.get(f"/students/{student_b.id}/marksheet")

        self.assertEqual(response_a.status_code, 200, response_a.text)
        self.assertEqual(response_b.status_code, 200, response_b.text)
        self.assertEqual(response_a.json()["overall"]["total_marks_obtained"], 92.0)
        self.assertEqual(response_b.json()["overall"]["total_marks_obtained"], 60.0)
        self.assertEqual(len(response_a.json()["exam_marks"][0]["subjects"]), 1)
        self.assertEqual(len(response_b.json()["exam_marks"][0]["subjects"]), 1)
