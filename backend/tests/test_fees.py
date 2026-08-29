import unittest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Fee, Student, User
from app.security import hash_password


class FeeApiTests(unittest.TestCase):
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
        self.student = self._create_student()
        self.student_2 = self._create_student(
            name="Grace Hopper",
            roll_number="ROLL-002",
            email="grace@example.com",
            phone="5550000002",
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

    def _create_fee(self, **overrides) -> Fee:
        payload = {
            "student_id": self.student.id,
            "amount": 5000.0,
            "paid_amount": 1000.0,
            "due_date": date(2026, 9, 30),
        }
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

    def test_create_fee_successfully(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 50000,
                "paid_amount": 10000,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["student_id"], self.student.id)
        self.assertEqual(body["amount"], 50000.0)
        self.assertEqual(body["paid_amount"], 10000.0)
        self.assertEqual(body["due_amount"], 40000.0)
        self.assertEqual(body["status"], "partial")
        self.assertIn("created_at", body)

    def test_create_fee_missing_student(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": 9999,
                "amount": 5000,
                "paid_amount": 1000,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 404, response.text)

    def test_create_fee_invalid_amount(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": -1,
                "paid_amount": 0,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_fee_negative_paid_amount(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 500,
                "paid_amount": -10,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_create_fee_paid_amount_exceeds_amount(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 500,
                "paid_amount": 600,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_pending_status_calculation(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 1000,
                "paid_amount": 0,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "pending")
        self.assertEqual(response.json()["due_amount"], 1000.0)

    def test_partial_status_calculation(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 1000,
                "paid_amount": 300,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "partial")
        self.assertEqual(response.json()["due_amount"], 700.0)

    def test_paid_status_calculation(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 1000,
                "paid_amount": 1000,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["status"], "paid")
        self.assertEqual(response.json()["due_amount"], 0.0)

    def test_due_amount_calculation(self):
        fee = self._create_fee(amount=4500.0, paid_amount=1500.0, due_date=date(2026, 8, 15))

        self._login(self.admin.email)
        response = self.client.get(f"/fees/{fee.id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["due_amount"], 3000.0)

    def test_get_fee_success(self):
        fee = self._create_fee(amount=3000.0, paid_amount=500.0)

        self._login(self.teacher.email)
        response = self.client.get(f"/fees/{fee.id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], fee.id)
        self.assertEqual(response.json()["student_id"], self.student.id)

    def test_get_missing_fee(self):
        self._login(self.teacher.email)

        response = self.client.get("/fees/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_unauthenticated_access_to_fee_endpoints(self):
        response = self.client.get("/fees")
        self.assertEqual(response.status_code, 401, response.text)

    def test_non_admin_cannot_create_fee(self):
        self._login(self.teacher.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 500,
                "paid_amount": 0,
                "due_date": "2026-09-30",
            },
        )

        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_update_fee(self):
        fee = self._create_fee()
        self._login(self.teacher.email)

        response = self.client.patch(
            f"/fees/{fee.id}",
            json={"paid_amount": 3000},
        )

        self.assertEqual(response.status_code, 403, response.text)

    def test_non_admin_cannot_delete_fee(self):
        fee = self._create_fee()
        self._login(self.teacher.email)

        response = self.client.delete(f"/fees/{fee.id}")

        self.assertEqual(response.status_code, 403, response.text)

    def test_admin_can_update_fee(self):
        fee = self._create_fee(amount=6000.0, paid_amount=2000.0)
        self._login(self.admin.email)

        response = self.client.patch(
            f"/fees/{fee.id}",
            json={"paid_amount": 6000},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["paid_amount"], 6000.0)
        self.assertEqual(response.json()["due_amount"], 0.0)
        self.assertEqual(response.json()["status"], "paid")

    def test_update_payment_changes_due_amount_and_status(self):
        fee = self._create_fee(amount=1000.0, paid_amount=300.0)
        self._login(self.admin.email)

        response = self.client.patch(
            f"/fees/{fee.id}",
            json={"paid_amount": 1000},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["due_amount"], 0.0)
        self.assertEqual(response.json()["status"], "paid")

    def test_update_amount_and_paid_amount_validation(self):
        fee = self._create_fee(amount=1000.0, paid_amount=200.0)
        self._login(self.admin.email)

        response = self.client.patch(
            f"/fees/{fee.id}",
            json={"amount": 100, "paid_amount": 200},
        )

        self.assertEqual(response.status_code, 422, response.text)

    def test_update_fee_missing_student(self):
        fee = self._create_fee()
        self._login(self.admin.email)

        response = self.client.patch(
            f"/fees/{fee.id}",
            json={"student_id": 9999},
        )

        self.assertEqual(response.status_code, 404, response.text)

    def test_delete_fee_success(self):
        fee = self._create_fee()
        self._login(self.admin.email)

        response = self.client.delete(f"/fees/{fee.id}")

        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.client.get(f"/fees/{fee.id}").status_code, 404)

    def test_delete_missing_fee(self):
        self._login(self.admin.email)

        response = self.client.delete("/fees/9999")

        self.assertEqual(response.status_code, 404, response.text)

    def test_list_fees(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 1, 15))
        self._create_fee(student_id=self.student_2.id, amount=7000, paid_amount=7000, due_date=date(2026, 2, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["total"], 2)
        self.assertEqual(len(body["items"]), 2)

    def test_filter_fees_by_student_id(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 1, 15))
        self._create_fee(student_id=self.student_2.id, amount=7000, paid_amount=7000, due_date=date(2026, 2, 15))
        self._login(self.teacher.email)

        response = self.client.get(f"/fees?student_id={self.student.id}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["student_id"], self.student.id)

    def test_filter_fees_by_status(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=5000, due_date=date(2026, 1, 15))
        self._create_fee(student_id=self.student_2.id, amount=7000, paid_amount=2000, due_date=date(2026, 2, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees?status=partial")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["status"], "partial")

    def test_filter_fees_by_due_date(self):
        target_date = date(2026, 8, 10)
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=target_date)
        self._create_fee(student_id=self.student_2.id, amount=7000, paid_amount=7000, due_date=date(2026, 9, 15))
        self._login(self.teacher.email)

        response = self.client.get(f"/fees?due_date={target_date.isoformat()}")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["due_date"], target_date.isoformat())

    def test_search_fees_by_student_name(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 1, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees?search=Ada")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["student_id"], self.student.id)

    def test_search_fees_by_roll_number(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 1, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees?search=ROLL-001")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["student_id"], self.student.id)

    def test_fee_pagination(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 1, 15))
        self._create_fee(student_id=self.student.id, amount=6000, paid_amount=2000, due_date=date(2026, 2, 15))
        self._create_fee(student_id=self.student.id, amount=7000, paid_amount=3000, due_date=date(2026, 3, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees?page=1&page_size=2")

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["page_size"], 2)
        self.assertEqual(body["total"], 3)
        self.assertEqual(body["total_pages"], 2)
        self.assertEqual(len(body["items"]), 2)

    def test_fee_deterministic_ordering(self):
        self._create_fee(student_id=self.student.id, amount=5000, paid_amount=1000, due_date=date(2026, 3, 15))
        self._create_fee(student_id=self.student_2.id, amount=7000, paid_amount=7000, due_date=date(2026, 1, 15))
        self._login(self.teacher.email)

        response = self.client.get("/fees")

        self.assertEqual(response.status_code, 200, response.text)
        due_dates = [item["due_date"] for item in response.json()["items"]]
        self.assertEqual(due_dates, ["2026-01-15", "2026-03-15"])

    def test_fee_response_shape_and_ignores_client_status_due_amount(self):
        self._login(self.admin.email)

        response = self.client.post(
            "/fees",
            json={
                "student_id": self.student.id,
                "amount": 1000,
                "paid_amount": 300,
                "due_date": "2026-09-30",
                "status": "paid",
                "due_amount": 999,
            },
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(
            list(body.keys()),
            [
                "id",
                "student_id",
                "amount",
                "paid_amount",
                "due_amount",
                "due_date",
                "status",
                "created_at",
            ],
        )
        self.assertEqual(body["due_amount"], 700.0)
        self.assertEqual(body["status"], "partial")
