from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


academic_class_subjects = Table(
    "academic_class_subjects",
    Base.metadata,
    Column("academic_class_id", ForeignKey("academic_classes.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
)

teacher_subjects = Table(
    "teacher_subjects",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
)

teacher_academic_classes = Table(
    "teacher_academic_classes",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("academic_class_id", ForeignKey("academic_classes.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="admin")

    student: Mapped["Student | None"] = relationship(
        back_populates="user",
        uselist=False,
    )
    teacher: Mapped["Teacher | None"] = relationship(
        back_populates="user",
        uselist=False,
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=True,
    )
    academic_class_id: Mapped[int | None] = mapped_column(
        ForeignKey("academic_classes.id"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100))
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    course: Mapped[str] = mapped_column(String(100))
    semester: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User | None] = relationship(back_populates="student")
    academic_class: Mapped["AcademicClass | None"] = relationship(
        back_populates="students"
    )
    marks: Mapped[list["Mark"]] = relationship(back_populates="student")
    attendances: Mapped[list["Attendance"]] = relationship(back_populates="student")
    fees: Mapped[list["Fee"]] = relationship(back_populates="student")
    assignment_submissions: Mapped[list["AssignmentSubmission"]] = relationship(
        back_populates="student"
    )


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    academic_class_id: Mapped[int] = mapped_column(
        ForeignKey("academic_classes.id"),
        index=True,
    )
    due_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subject: Mapped["Subject"] = relationship(back_populates="assignments")
    academic_class: Mapped["AcademicClass"] = relationship(back_populates="assignments")
    submissions: Mapped[list["AssignmentSubmission"]] = relationship(
        back_populates="assignment"
    )


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "student_id",
            name="uq_assignment_submissions_assignment_student",
        ),
        CheckConstraint(
            "status IN ('pending', 'submitted', 'late')",
            name="ck_assignment_submissions_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id"),
        index=True,
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20))

    assignment: Mapped[Assignment] = relationship(back_populates="submissions")
    student: Mapped[Student] = relationship(back_populates="assignment_submissions")


class Fee(Base):
    __tablename__ = "fees"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_fees_amount_non_negative"),
        CheckConstraint("paid_amount >= 0", name="ck_fees_paid_amount_non_negative"),
        CheckConstraint("paid_amount <= amount", name="ck_fees_paid_amount_lte_amount"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[Student] = relationship(back_populates="fees")

    @property
    def due_amount(self) -> float:
        return float(self.amount - self.paid_amount)

    @property
    def status(self) -> str:
        if self.paid_amount == 0:
            return "pending"
        if 0 < self.paid_amount < self.amount:
            return "partial"
        if self.paid_amount == self.amount:
            return "paid"
        return "pending"


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20))

    user: Mapped[User] = relationship(back_populates="teacher")
    subjects: Mapped[list["Subject"]] = relationship(
        secondary=teacher_subjects,
        back_populates="teachers",
    )
    academic_classes: Mapped[list["AcademicClass"]] = relationship(
        secondary=teacher_academic_classes,
        back_populates="teachers",
    )


class AcademicClass(Base):
    __tablename__ = "academic_classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    course: Mapped[str] = mapped_column(String(100))
    semester: Mapped[int] = mapped_column(Integer)

    students: Mapped[list[Student]] = relationship(back_populates="academic_class")
    subjects: Mapped[list["Subject"]] = relationship(
        secondary=academic_class_subjects,
        back_populates="academic_classes",
    )
    teachers: Mapped[list[Teacher]] = relationship(
        secondary=teacher_academic_classes,
        back_populates="academic_classes",
    )
    exams: Mapped[list["Exam"]] = relationship(back_populates="academic_class")
    assignments: Mapped[list[Assignment]] = relationship(back_populates="academic_class")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True)

    marks: Mapped[list["Mark"]] = relationship(back_populates="subject")
    academic_classes: Mapped[list[AcademicClass]] = relationship(
        secondary=academic_class_subjects,
        back_populates="subjects",
    )
    teachers: Mapped[list[Teacher]] = relationship(
        secondary=teacher_subjects,
        back_populates="subjects",
    )
    assignments: Mapped[list[Assignment]] = relationship(back_populates="subject")


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    exam_type: Mapped[str] = mapped_column(String(50))
    exam_date: Mapped[date] = mapped_column(Date, index=True)
    academic_class_id: Mapped[int] = mapped_column(
        ForeignKey("academic_classes.id"),
        index=True,
    )

    academic_class: Mapped[AcademicClass] = relationship(back_populates="exams")
    marks: Mapped[list["Mark"]] = relationship(back_populates="exam")


class Attendance(Base):
    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "attendance_date",
            name="uq_attendances_student_date",
        ),
        CheckConstraint(
            "status IN ('present', 'absent')",
            name="ck_attendances_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20))

    student: Mapped[Student] = relationship(back_populates="attendances")


class Mark(Base):
    __tablename__ = "marks"
    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "student_id",
            "subject_id",
            name="uq_marks_exam_student_subject",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    marks: Mapped[float] = mapped_column(Float)

    exam: Mapped["Exam"] = relationship(back_populates="marks")
    student: Mapped[Student] = relationship(back_populates="marks")
    subject: Mapped[Subject] = relationship(back_populates="marks")
