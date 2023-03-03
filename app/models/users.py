import datetime
import hashlib
import uuid
from typing import Optional, Union, TYPE_CHECKING

from fastapi import HTTPException
from pydantic import validator
from sqlmodel import Field, Session, Relationship, select, SQLModel

from app.core.enums import Role, Degree

if TYPE_CHECKING:
    from models.articles import Article


class UserBase(SQLModel):
    email: str = Field(index=True, nullable=False)
    role: Role


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(primary_key=True, index=True, nullable=False)
    hashed_password: Optional[str] = Field(max_length=256)
    admin: "Admin" = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    teacher: "Teacher" = Relationship(back_populates="user",
                                      sa_relationship_kwargs={"uselist": False})
    student: "Student" = Relationship(back_populates="user",
                                      sa_relationship_kwargs={"uselist": False})
    articles: list["Article"] = Relationship(back_populates="author")
    is_staff: bool = Field(default=False)

    def __repr__(self):
        return f"<{self.id}: {self.email}>"

    class Config:
        arbitrary_types_allowed = True

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

    def set_profile(self, profile: "Profile"):
        if self.role == Role.admin:
            self.admin = profile
        elif self.role == Role.teacher:
            self.teacher = profile
        elif self.role == Role.student:
            self.student = profile
        else:
            raise ValueError(f"Unknown role: {self.role}")

    def set_password(self, plain_password: str):
        salt = uuid.uuid4().hex
        self.hashed_password = hashlib.sha512((plain_password).encode()).hexdigest() + salt

    def check_password(self, plain_password: str) -> bool:
        salt = self.hashed_password[-32:]
        return self.hashed_password == hashlib.sha512((plain_password).encode()).hexdigest() + salt


class UserRead(UserBase):
    id: int
    profile: "FullProfile"


class UserCreate(UserBase):
    password: str
    profile: "ProfileCreate"

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # validate that password has both letters and numbers
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v


class TeacherStudent(SQLModel, table=True):
    __tablename__ = "teacher_student"
    teacher_id: Optional[int] = Field(index=True, primary_key=True, foreign_key="teachers.id")
    student_id: Optional[int] = Field(index=True, primary_key=True, foreign_key="students.id")


class AdminBase(SQLModel):
    full_name: str = Field(min_length=4)


class Admin(AdminBase, table=True):
    __tablename__ = "admins"
    id: Optional[int] = Field(primary_key=True, index=True, nullable=False)
    user_id: Optional[int] = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="admin")


class AdminCreate(AdminBase):
    pass


class TeacherBase(SQLModel):
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    degree: Degree


class Teacher(TeacherBase, table=True):
    __tablename__ = "teachers"
    id: Optional[int] = Field(primary_key=True, index=True, nullable=False)
    user_id: Optional[int] = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="teacher")
    students: list["Student"] = Relationship(
        link_model=TeacherStudent,
        back_populates="teachers"
    )


class TeacherCreate(TeacherBase):
    pass


class StudentBase(SQLModel):
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    entry_date: datetime.date


class Student(StudentBase, table=True):
    __tablename__ = "students"
    id: Optional[int] = Field(primary_key=True, index=True, nullable=False)
    user_id: Optional[int] = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="student")
    teachers: list[Teacher] = Relationship(link_model=TeacherStudent, back_populates="students")


class StudentWithTeachers(StudentBase):
    teachers: list[Teacher]


class StudentCreate(StudentBase):
    teachers: list[int]

    @validator("teachers")
    def one_or_more(cls, value):
        if len(value) < 1:
            raise ValueError("Must have at least one associated teacher")
        return value

    @validator("entry_date")
    def entry_date_must_be_in_past(cls, value):
        if value > datetime.date.today():
            raise ValueError("Entry date must be in the past")
        return value


Profile = Union[Admin, Teacher, Student]
FullProfile = Union[Admin, Teacher, StudentWithTeachers]
ProfileCreate = Union[AdminCreate, TeacherCreate, StudentCreate]

UserCreate.update_forward_refs()
UserRead.update_forward_refs()


def profile_model_factory(role: Role, profile_data: ProfileCreate, session: Session) -> Profile:
    if role == Role.admin:
        return Admin.from_orm(profile_data)
    elif role == Role.teacher:
        return Teacher.from_orm(profile_data)
    elif role == Role.student:
        query = select(Teacher).where(Teacher.id.in_(profile_data.teachers))
        teachers = session.exec(query).all()

        if not teachers:
            raise HTTPException(
                status_code=400, detail="Teachers with provided ids not found"
            )
        student = Student.from_orm(profile_data)
        student.teachers = [t for t in teachers]
        return student
    else:
        raise ValueError("Invalid role")
