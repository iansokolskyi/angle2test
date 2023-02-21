from fastapi import HTTPException
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Enum,
    Table,
)
from sqlalchemy.orm import relationship, Session, mapped_column

from app.core.db import Base
from app.core.enums import Role, Degree


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(Enum(Role), nullable=False)
    admin = relationship("Admin", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)
    articles = relationship("Article", back_populates="author", uselist=True)

    def __repr__(self):
        return f"<{self.id}: {self.email}>"

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, plain_password):
        self.hashed_password = hash(plain_password)

    @property
    def profile(self):
        if self.role == Role.admin:
            return self.admin
        elif self.role == Role.teacher:
            return self.teacher
        elif self.role == Role.student:
            return self.student
        else:
            raise ValueError(f"Unknown role: {self.role}")

    @profile.setter
    def profile(self, profile):
        if self.role == Role.admin:
            self.admin = profile
        elif self.role == Role.teacher:
            self.teacher = profile
        elif self.role == Role.student:
            self.student = profile
        else:
            raise ValueError(f"Unknown role: {self.role}")


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="admin")


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = mapped_column(String, use_existing_column=True)
    last_name = mapped_column(String, use_existing_column=True)
    degree = Column(Enum(Degree))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="teacher")
    students = relationship(
        "Student", secondary="teacher_student", back_populates="teachers"
    )


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    first_name = mapped_column(String, use_existing_column=True)
    last_name = mapped_column(String, use_existing_column=True)
    entry_date = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="student")
    teachers = relationship("Teacher", secondary="teacher_student")


teacher_student = Table(
    "teacher_student",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.id")),
    Column("student_id", Integer, ForeignKey("students.id")),
)


def profile_model_factory(role: Role, data: dict, db_session: Session):
    if role == Role.admin:
        return Admin(**data)
    elif role == Role.teacher:
        return Teacher(**data)
    elif role == Role.student:
        teachers = data.pop("teachers")
        student = Student(**data)
        teachers = db_session.query(Teacher).filter(Teacher.id.in_(teachers)).all()
        if not teachers:
            raise HTTPException(
                status_code=400, detail="Teachers with provided ids not found"
            )
        student.teachers = teachers
        return student
    else:
        raise ValueError("Invalid role")
