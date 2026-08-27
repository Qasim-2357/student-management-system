from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Table, Column
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


class Mark(Base):
    __tablename__ = "marks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    marks: Mapped[float] = mapped_column(Float)

    student: Mapped[Student] = relationship(back_populates="marks")
    subject: Mapped[Subject] = relationship(back_populates="marks")
