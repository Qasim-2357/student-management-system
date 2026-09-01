import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Exam, Student, Subject, Teacher, User
from app.security import hash_password


class MarkApiTests(unittest.TestCase):
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
        self.academic_class = self._create_academic_class()
        self.exam = self._create_exam()
        self.student = self._create_student()
        self.subject = self._create_subject()
        self.teacher = Teacher(
            user_id=self.teacher_user.id,
            name="Teacher One",
            email="teacher-profile@example.com",
            phone="5557654321",
        )
        self.teacher.academic_classes.append(self.academic_class)
        self.teacher.subjects.append(self.subject)
        self.db.add(self.teacher)
        self.db.commit()

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

    def _create_exam(self, **overrides) -> Exam:
        payload = {
            "name": "Midterm",
            "exam_type": "midterm",
            "exam_date": date(2026, 1, 15),
            "academic_class_id": self.academic_class.id,
        }
        payload.update(overrides)
        exam = Exam(**payload)
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

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

    def _create_subject(self, **overrides) -> Subject:
        payload = {
            "name": "Mathematics",
            "code": "MATH-101",
        }
        payload.update(overrides)
        subject = Subject(**payload)
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return subject

    def _login(self, email: str):
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def _mark_payload(self, **overrides):
        payload = {
            "exam_id": self.exam.id,
            "student_id": self.student.id,
            "subject_id": self.subject.id,
            "marks": 87.5,
        }
        payload.update(overrides)
        return payload

    def _create_mark_as_admin(self, **overrides):
        self._login(self.admin.email)
        return self.client.post("/marks", json=self._mark_payload(**overrides))

    # ---- create ----

    def test_create_mark(self):
        response = self._create_mark_as_admin()

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["exam_id"], self.exam.id)
        self.assertEqual(response.json()["student_id"], self.student.id)
        self.assertEqual(response.json()["subject_id"], self.subject.id)
        self.assertEqual(response.json()["marks"], 87.5)

    def test_create_requires_exam_id(self):
        self._login(self.admin.email)
        payload = self._mark_payload()
        del payload["exam_id"]

        response = self.client.post("/marks", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_student_id(self):
        self._login(self.admin.email)
        payload = self._mark_payload()
        del payload["student_id"]

        response = self.client.post("/marks", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_subject_id(self):
        self._login(self.admin.email)
        payload = self._mark_payload()
        del payload["subject_id"]

        response = self.client.post("/marks", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_requires_marks(self):
        self._login(self.admin.email)
        payload = self._mark_payload()
        del payload["marks"]

        response = self.client.post("/marks", json=payload)

        self.assertEqual(response.status_code, 422, response.text)

    def test_marks_below_zero_rejected(self):
        response = self._create_mark_as_admin(marks=-1)

        self.assertEqual(response.status_code, 422, response.text)

    def test_marks_above_hundred_rejected(self):
        response = self._create_mark_as_admin(marks=101)

        self.assertEqual(response.status_code, 422, response.text)

    def test_marks_boundary_values_accepted(self):
        self.assertEqual(self._create_mark_as_admin(marks=0).status_code, 201)
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        response = self._create_mark_as_admin(marks=100, subject_id=other_subject.id)

        self.assertEqual(response.status_code, 201, response.text)

    def test_create_rejects_missing_exam(self):
        response = self._create_mark_as_admin(exam_id=9999)

        self.assertEqual(response.status_code, 404, response.text)

    def test_create_rejects_missing_student(self):
        response = self._create_mark_as_admin(student_id=9999)

        self.assertEqual(response.status_code, 404, response.text)

    def test_create_rejects_missing_subject(self):
        response = self._create_mark_as_admin(subject_id=9999)

        self.assertEqual(response.status_code, 404, response.text)

    def test_duplicate_combination_rejected(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)

        response = self._create_mark_as_admin(marks=50)

        self.assertEqual(response.status_code, 409, response.text)

    def test_same_student_subject_different_exam_allowed(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        other_exam = self._create_exam(name="Final", exam_type="final", exam_date=date(2026, 5, 1))

        response = self._create_mark_as_admin(exam_id=other_exam.id)

        self.assertEqual(response.status_code, 201, response.text)

    # ---- read ----

    def test_get_mark(self):
        create_response = self._create_mark_as_admin()
        mark_id = create_response.json()["id"]

        response = self.client.get(f"/marks/{mark_id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], mark_id)

    def test_get_mark_not_found(self):
        self._login(self.admin.email)

        response = self.client.get("/marks/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_authenticated_teacher_can_read_marks(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        self._login(self.teacher_user.email)

        response = self.client.get("/marks")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_unauthenticated_read_rejected(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        self.client.cookies.clear()

        response = self.client.get("/marks")

        self.assertEqual(response.status_code, 401, response.text)

    def test_unauthenticated_get_by_id_rejected(self):
        mark_id = self._create_mark_as_admin().json()["id"]
        self.client.cookies.clear()

        response = self.client.get(f"/marks/{mark_id}")

        self.assertEqual(response.status_code, 401, response.text)

    # ---- update ----

    def test_update_mark(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"marks": 95.0})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["marks"], 95.0)

    def test_partial_update_marks_only(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"marks": 60})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["marks"], 60)
        self.assertEqual(response.json()["exam_id"], self.exam.id)

    def test_update_rejects_invalid_marks(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"marks": 150})

        self.assertEqual(response.status_code, 422, response.text)

    def test_update_rejects_missing_exam(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"exam_id": 9999})

        self.assertEqual(response.status_code, 404, response.text)

    def test_update_rejects_missing_student(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"student_id": 9999})

        self.assertEqual(response.status_code, 404, response.text)

    def test_update_rejects_missing_subject(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(f"/marks/{mark_id}", json={"subject_id": 9999})

        self.assertEqual(response.status_code, 404, response.text)

    def test_update_rejects_duplicate_combination(self):
        self._create_mark_as_admin()
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        second_mark_id = self._create_mark_as_admin(subject_id=other_subject.id).json()["id"]

        response = self.client.patch(
            f"/marks/{second_mark_id}",
            json={"subject_id": self.subject.id},
        )

        self.assertEqual(response.status_code, 409, response.text)

    def test_update_same_combination_on_same_mark_allowed(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.patch(
            f"/marks/{mark_id}",
            json={
                "exam_id": self.exam.id,
                "student_id": self.student.id,
                "subject_id": self.subject.id,
                "marks": 72.0,
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["marks"], 72.0)

    def test_update_not_found(self):
        self._login(self.admin.email)

        response = self.client.patch("/marks/9999", json={"marks": 50})

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_update(self):
        mark_id = self._create_mark_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.patch(f"/marks/{mark_id}", json={"marks": 10})

        self.assertEqual(response.status_code, 403, response.text)

    # ---- delete ----

    def test_delete_mark(self):
        mark_id = self._create_mark_as_admin().json()["id"]

        response = self.client.delete(f"/marks/{mark_id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/marks/{mark_id}").status_code, 404)

    def test_delete_not_found(self):
        self._login(self.admin.email)

        response = self.client.delete("/marks/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthorized_delete(self):
        mark_id = self._create_mark_as_admin().json()["id"]
        self._login(self.teacher_user.email)

        response = self.client.delete(f"/marks/{mark_id}")

        self.assertEqual(response.status_code, 403, response.text)

    # ---- writes require admin ----

    def test_unauthorized_write(self):
        self._login(self.teacher_user.email)

        response = self.client.post("/marks", json=self._mark_payload())

        self.assertEqual(response.status_code, 403, response.text)

    def test_unauthenticated_write(self):
        response = self.client.post("/marks", json=self._mark_payload())

        self.assertEqual(response.status_code, 401, response.text)

    # ---- search / filters / pagination ----

    def test_search_by_student_name(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        other_student = self._create_student(
            name="Grace Hopper", roll_number="ROLL-002", email="grace@example.com"
        )
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        self.assertEqual(
            self._create_mark_as_admin(
                student_id=other_student.id, subject_id=other_subject.id
            ).status_code,
            201,
        )

        response = self.client.get("/marks", params={"search": "grace"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["student_id"], other_student.id)

    def test_search_by_subject_code(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)

        response = self.client.get("/marks", params={"search": "MATH-101"})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)

    def test_filter_by_exam_id(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        other_exam = self._create_exam(name="Final", exam_type="final", exam_date=date(2026, 5, 1))
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        self.assertEqual(
            self._create_mark_as_admin(
                exam_id=other_exam.id, subject_id=other_subject.id
            ).status_code,
            201,
        )

        response = self.client.get("/marks", params={"exam_id": other_exam.id})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["exam_id"], other_exam.id)

    def test_filter_by_student_id(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        other_student = self._create_student(
            name="Grace Hopper", roll_number="ROLL-002", email="grace@example.com"
        )
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        self.assertEqual(
            self._create_mark_as_admin(
                student_id=other_student.id, subject_id=other_subject.id
            ).status_code,
            201,
        )

        response = self.client.get("/marks", params={"student_id": other_student.id})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["student_id"], other_student.id)

    def test_filter_by_subject_id(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        other_subject = self._create_subject(name="Physics", code="PHY-101")
        self.assertEqual(
            self._create_mark_as_admin(subject_id=other_subject.id).status_code,
            201,
        )

        response = self.client.get("/marks", params={"subject_id": other_subject.id})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["subject_id"], other_subject.id)

    def test_pagination(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        for index in range(2):
            subject = self._create_subject(name=f"Subject {index}", code=f"SUB-{index}")
            response = self._create_mark_as_admin(subject_id=subject.id)
            self.assertEqual(response.status_code, 201, response.text)

        response = self.client.get("/marks", params={"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 3)
        self.assertEqual(response.json()["total_pages"], 2)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_pagination_deterministic_ordering(self):
        self.assertEqual(self._create_mark_as_admin().status_code, 201)
        for index in range(2):
            subject = self._create_subject(name=f"Subject {index}", code=f"SUB-{index}")
            self._create_mark_as_admin(subject_id=subject.id)

        first = self.client.get("/marks")
        second = self.client.get("/marks")

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