from datetime import date
from typing import Union

from pydantic import BaseModel, validator, Field

from app.core.enums import Degree, Role


class AdminProfileSchema(BaseModel):
    class Config:
        orm_mode = True

    full_name: str = Field(..., min_length=4)


class TeacherProfileSchema(BaseModel):
    class Config:
        orm_mode = True

    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    degree: Degree


class StudentBaseSchema(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    entry_date: date

    class Config:
        orm_mode = True


class StudentProfileSchema(StudentBaseSchema):
    class Config:
        orm_mode = True

    teachers: list[TeacherProfileSchema]


class StudentCreateProfileSchema(StudentBaseSchema):
    teachers: list[int]

    @validator("teachers")
    def one_or_more(cls, value):
        if len(value) < 1:
            raise ValueError("Must have at least one associated teacher")
        return value

    @validator("entry_date")
    def entry_date_must_be_in_past(cls, value):
        if value > date.today():
            raise ValueError("Entry date must be in the past")
        return value

    @validator("first_name", "last_name")
    def min_length(cls, value, field):
        if len(value) < 2:
            raise ValueError(f"{field.name} must be at least 2 characters long")
        return value


class UserBaseSchema(BaseModel):
    email: str
    profile: Union[AdminProfileSchema, TeacherProfileSchema, StudentProfileSchema]
    role: Role


class UserSchema(UserBaseSchema):
    id: int

    class Config:
        orm_mode = True


class UserCreateSchema(UserBaseSchema):
    password: str
    profile: Union[AdminProfileSchema, TeacherProfileSchema, StudentCreateProfileSchema]

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


def profile_schema_factory(role):
    if role == Role.admin:
        return AdminProfileSchema
    elif role == Role.teacher:
        return TeacherProfileSchema
    elif role == Role.student:
        return StudentCreateProfileSchema
    else:
        raise ValueError("Invalid role")
