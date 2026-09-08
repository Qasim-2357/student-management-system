import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.models import Student, Teacher, User
from app.security import hash_password


class AuthIdentifierLoginTests(unittest.TestCase):
    """Covers the institutional-identifier login contract: STU-XXXX,
    TCH-XXXX and ADM-XXXX resolving to the correct User, alongside the
    legacy email backward-compatibility path."""

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

        self.admin_user = self._create_user(
            "registrar@studentsphere.edu", "admin", password="AdminPass@123"
        )

        self.student_user = self._create_user(
            "priya.sharma@studentsphere.edu", "student", password="StudentPass@123"
        )
        self.student = Student(
            user_id=self.student_user.id,
            name="Priya Sharma",
            roll_number="ROLL-001",
            email="priya.sharma@studentsphere.edu",
            phone="5551234567",
            course="Computer Science",
            semester=3,
        )
        self.db.add(self.student)
        self.db.commit()
        self.db.refresh(self.student)

        self.teacher_user = self._create_user(
            "qasim.khan@studentsphere.edu", "teacher", password="TeacherPass@123"
        )
        self.teacher = Teacher(
            user_id=self.teacher_user.id,
            name="Qasim Khan",
            email="qasim.khan-profile@studentsphere.edu",
            phone="5557654321",
        )
        self.db.add(self.teacher)
        self.db.commit()
        self.db.refresh(self.teacher)

        # A non-admin user whose numeric id we can address with an ADM-
        # prefix to prove role is never trusted from the identifier alone.
        self.other_student_user = self._create_user(
            "second.student@studentsphere.edu", "student", password="Password@123"
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

    def _create_user(self, email: str, role: str, password: str = "Password@123") -> User:
        user = User(
            name=role.title(),
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ---- institutional identifier login ----

    def test_student_can_login_with_student_code(self):
        response = self.client.post(
            "/auth/login",
            json={"identifier": self.student.student_code, "password": "StudentPass@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()["user"]
        self.assertEqual(body["id"], self.student_user.id)
        self.assertEqual(body["role"], "student")

    def test_teacher_can_login_with_teacher_code(self):
        response = self.client.post(
            "/auth/login",
            json={"identifier": self.teacher.teacher_code, "password": "TeacherPass@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()["user"]
        self.assertEqual(body["id"], self.teacher_user.id)
        self.assertEqual(body["role"], "teacher")

    def test_admin_can_login_with_admin_code(self):
        admin_code = f"ADM-{self.admin_user.id:04d}"
        response = self.client.post(
            "/auth/login",
            json={"identifier": admin_code, "password": "AdminPass@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()["user"]
        self.assertEqual(body["id"], self.admin_user.id)
        self.assertEqual(body["role"], "admin")

    def test_identifier_matching_is_case_insensitive_and_trimmed(self):
        response = self.client.post(
            "/auth/login",
            json={
                "identifier": f"  {self.student.student_code.lower()}  ",
                "password": "StudentPass@123",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["user"]["id"], self.student_user.id)

    def test_admin_code_pointing_at_non_admin_user_is_rejected(self):
        # The numeric id belongs to a real user, but that user is a
        # student, not an admin - the ADM- prefix must not grant admin
        # access just because the id happens to exist.
        non_admin_code = f"ADM-{self.other_student_user.id:04d}"
        response = self.client.post(
            "/auth/login",
            json={"identifier": non_admin_code, "password": "Password@123"},
        )
        self.assertEqual(response.status_code, 401, response.text)

    def test_unknown_identifier_returns_generic_authentication_failure(self):
        response = self.client.post(
            "/auth/login",
            json={"identifier": "STU-9999", "password": "whatever"},
        )
        self.assertEqual(response.status_code, 401, response.text)
        unknown_detail = response.json()["detail"]

        wrong_password_response = self.client.post(
            "/auth/login",
            json={"identifier": self.student.student_code, "password": "wrong-password"},
        )
        self.assertEqual(wrong_password_response.status_code, 401, wrong_password_response.text)

        # Same generic message whether the identifier doesn't exist or the
        # password is simply wrong - existence must not be revealed.
        self.assertEqual(unknown_detail, wrong_password_response.json()["detail"])

    def test_malformed_identifier_falls_back_to_email_lookup_and_fails(self):
        response = self.client.post(
            "/auth/login",
            json={"identifier": "not-a-real-identifier", "password": "whatever"},
        )
        self.assertEqual(response.status_code, 401, response.text)

    def test_missing_identifier_and_email_is_rejected(self):
        response = self.client.post(
            "/auth/login",
            json={"password": "whatever"},
        )
        self.assertEqual(response.status_code, 422, response.text)

    def test_get_current_user_reflects_database_role_not_client_input(self):
        login_response = self.client.post(
            "/auth/login",
            json={"identifier": self.student.student_code, "password": "StudentPass@123"},
        )
        self.assertEqual(login_response.status_code, 200, login_response.text)

        me_response = self.client.get("/auth/me")
        self.assertEqual(me_response.status_code, 200, me_response.text)
        self.assertEqual(me_response.json()["role"], "student")

        # An admin-only endpoint must still reject this session, proving the
        # role used for authorization comes from the User row (fetched via
        # get_current_user), not anything implied by the login identifier.
        admin_only_response = self.client.get("/dashboard/overview")
        self.assertEqual(admin_only_response.status_code, 403, admin_only_response.text)

    # ---- legacy email backward compatibility ----

    def test_legacy_email_field_still_logs_in(self):
        response = self.client.post(
            "/auth/login",
            json={"email": self.admin_user.email, "password": "AdminPass@123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["user"]["id"], self.admin_user.id)

    def test_identifier_takes_priority_over_email_when_both_supplied(self):
        response = self.client.post(
            "/auth/login",
            json={
                "identifier": self.student.student_code,
                "email": self.admin_user.email,
                "password": "StudentPass@123",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["user"]["id"], self.student_user.id)