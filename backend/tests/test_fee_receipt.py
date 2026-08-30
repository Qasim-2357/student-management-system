import unittest
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import AcademicClass, Fee, Student, User
from app.security import hash_password


class FeeReceiptApiTests(unittest.TestCase):
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
        self.admin = self._create_user()

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

    def _create_user(self):
        user = User(
            name="Admin",
            email=f"admin-{self._suffix()}@example.com",
            password_hash=hash_password("Password@123"),
            role="admin",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

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

    def _create_student(self, academic_class_id=None):
        student = Student(
            name="Ada Lovelace",
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

    def _create_fee(self, student_id, amount=500.0, paid_amount=200.0):
        fee = Fee(
            student_id=student_id,
            amount=amount,
            paid_amount=paid_amount,
            due_date=date(2026, 12, 31),
        )
        self.db.add(fee)
        self.db.commit()
        self.db.refresh(fee)
        return fee

    def _login(self):
        response = self.client.post(
            "/auth/login",
            json={"email": self.admin.email, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)

    def test_successful_receipt_response(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        response = self.client.get(f"/fees/{fee.id}/receipt")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["fee"]["id"], fee.id)

    def test_receipt_requires_authentication(self):
        student = self._create_student()
        fee = self._create_fee(student.id)

        response = self.client.get(f"/fees/{fee.id}/receipt")

        self.assertEqual(response.status_code, 401, response.text)

    def test_missing_fee_returns_404(self):
        self._login()

        response = self.client.get("/fees/9999/receipt")

        self.assertEqual(response.status_code, 404, response.text)

    def test_receipt_contains_fee_information(self):
        student = self._create_student()
        fee = self._create_fee(student.id, amount=750.0, paid_amount=250.0)
        self._login()

        body = self.client.get(f"/fees/{fee.id}/receipt").json()

        self.assertEqual(
            body["fee"],
            {
                "id": fee.id,
                "student_id": student.id,
                "amount": 750.0,
                "paid_amount": 250.0,
                "due_amount": 500.0,
                "due_date": "2026-12-31",
                "status": "partial",
                "created_at": body["fee"]["created_at"],
            },
        )

    def test_receipt_contains_student_information(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        body = self.client.get(f"/fees/{fee.id}/receipt").json()["student"]

        self.assertEqual(body["id"], student.id)
        self.assertEqual(body["name"], student.name)
        self.assertEqual(body["roll_number"], student.roll_number)
        self.assertEqual(body["email"], student.email)
        self.assertEqual(body["phone"], student.phone)
        self.assertEqual(body["course"], student.course)
        self.assertEqual(body["semester"], student.semester)

    def test_receipt_contains_class_information(self):
        academic_class = self._create_class()
        student = self._create_student(academic_class.id)
        fee = self._create_fee(student.id)
        self._login()

        body = self.client.get(f"/fees/{fee.id}/receipt").json()

        self.assertEqual(body["academic_class"]["id"], academic_class.id)
        self.assertEqual(body["academic_class"]["name"], academic_class.name)
        self.assertEqual(body["academic_class"]["code"], academic_class.code)
        self.assertEqual(body["academic_class"]["course"], academic_class.course)
        self.assertEqual(body["academic_class"]["semester"], academic_class.semester)

    def test_receipt_without_class_returns_null_class(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        body = self.client.get(f"/fees/{fee.id}/receipt").json()

        self.assertIsNone(body["academic_class"])

    def test_receipt_calculates_due_amount_and_paid_status(self):
        student = self._create_student()
        fee = self._create_fee(student.id, amount=1000.0, paid_amount=1000.0)
        self._login()

        receipt_fee = self.client.get(f"/fees/{fee.id}/receipt").json()["fee"]

        self.assertEqual(receipt_fee["due_amount"], 0.0)
        self.assertEqual(receipt_fee["status"], "paid")

    def test_receipt_reports_pending_fee(self):
        student = self._create_student()
        fee = self._create_fee(student.id, amount=1000.0, paid_amount=0.0)
        self._login()

        receipt_fee = self.client.get(f"/fees/{fee.id}/receipt").json()["fee"]

        self.assertEqual(receipt_fee["due_amount"], 1000.0)
        self.assertEqual(receipt_fee["status"], "pending")

    def test_receipt_response_shape(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        body = self.client.get(f"/fees/{fee.id}/receipt").json()

        self.assertEqual(set(body), {"fee", "student", "academic_class"})
        self.assertEqual(
            set(body["fee"]),
            {
                "id",
                "student_id",
                "amount",
                "paid_amount",
                "due_amount",
                "due_date",
                "status",
                "created_at",
            },
        )
        self.assertEqual(
            set(body["student"]),
            {"id", "name", "roll_number", "email", "phone", "course", "semester"},
        )

    def test_receipt_uses_fee_student_relationship(self):
        student_a = self._create_student()
        student_b = self._create_student()
        fee_a = self._create_fee(student_a.id, amount=300.0, paid_amount=100.0)
        self._create_fee(student_b.id, amount=900.0, paid_amount=900.0)
        self._login()

        body = self.client.get(f"/fees/{fee_a.id}/receipt").json()

        self.assertEqual(body["fee"]["student_id"], student_a.id)
        self.assertEqual(body["student"]["id"], student_a.id)
        self.assertNotEqual(body["student"]["id"], student_b.id)
        self.assertEqual(body["fee"]["amount"], 300.0)
