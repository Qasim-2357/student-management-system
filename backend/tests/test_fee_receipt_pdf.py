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


class FeeReceiptPdfApiTests(unittest.TestCase):
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

    def _create_fee(self, student_id):
        fee = Fee(
            student_id=student_id,
            amount=750.0,
            paid_amount=250.0,
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

    def test_successful_pdf_response(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        response = self.client.get(f"/fees/{fee.id}/receipt/pdf")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_pdf_content_type(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        response = self.client.get(f"/fees/{fee.id}/receipt/pdf")

        self.assertEqual(response.headers["content-type"], "application/pdf")

    def test_pdf_content_disposition_contains_expected_filename(self):
        student = self._create_student()
        fee = self._create_fee(student.id)
        self._login()

        response = self.client.get(f"/fees/{fee.id}/receipt/pdf")

        self.assertIn(
            f'filename="fee-receipt-{fee.id}.pdf"',
            response.headers["content-disposition"],
        )

    def test_pdf_uses_fee_student_and_class_information(self):
        academic_class = self._create_class()
        student = self._create_student(academic_class.id)
        fee = self._create_fee(student.id)
        self._login()

        response = self.client.get(f"/fees/{fee.id}/receipt/pdf")
        pdf_bytes = response.content

        self.assertGreater(len(pdf_bytes), 500)
        self.assertIn(b"Fee Receipt", pdf_bytes)
        self.assertIn(str(fee.id).encode(), pdf_bytes)
        self.assertIn(student.name.encode(), pdf_bytes)
        self.assertIn(student.roll_number.encode(), pdf_bytes)
        self.assertIn(academic_class.name.encode(), pdf_bytes)
        self.assertIn(b"750.00", pdf_bytes)
        self.assertIn(b"250.00", pdf_bytes)
        self.assertIn(b"500.00", pdf_bytes)
        self.assertIn(b"partial", pdf_bytes)
        self.assertIn(b"2026-12-31", pdf_bytes)

    def test_missing_fee_returns_404(self):
        self._login()

        response = self.client.get("/fees/9999/receipt/pdf")

        self.assertEqual(response.status_code, 404, response.text)

    def test_pdf_requires_authentication(self):
        student = self._create_student()
        fee = self._create_fee(student.id)

        response = self.client.get(f"/fees/{fee.id}/receipt/pdf")

        self.assertEqual(response.status_code, 401, response.text)

    def test_pdf_uses_the_requested_fee_record(self):
        student = self._create_student()
        requested_fee = self._create_fee(student.id)
        other_fee = Fee(
            student_id=student.id,
            amount=1200.0,
            paid_amount=1200.0,
            due_date=date(2027, 1, 31),
        )
        self.db.add(other_fee)
        self.db.commit()
        self._login()

        response = self.client.get(f"/fees/{requested_fee.id}/receipt/pdf")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn(b"750.00", response.content)
        self.assertNotIn(b"1200.00", response.content)
