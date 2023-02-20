from typing import Union, Type

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.users import User, profile_model_factory
from app.schemas.users import (
    UserCreateSchema,
    Role,
    profile_schema_factory,
)


def get_user_by_id(user_id: int, db_session: Session) -> Union[User, None]:
    return db_session.query(User).filter(User.id == user_id).first()


def create_user(user: UserCreateSchema, db_session: Session) -> User:
    if db_session.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    user_data = user.dict()
    profile_data = user_data.pop("profile")

    password = user_data.pop("password")
    db_user = User(**user_data)
    db_user.password = password
    db_user = assign_profile_to_user(db_user, profile_data, db_session=db_session)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def assign_profile_to_user(user: User, profile_data: dict, db_session: Session) -> User:
    try:
        profile = profile_schema_factory(user.role)(**profile_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    db_profile = profile_model_factory(user.role, profile.dict(), db_session=db_session)
    user.profile = db_profile
    return user


def get_users_by_role(role: Role, db_session: Session) -> list[Type[User]]:
    return db_session.query(User).filter(User.role == role).all()


def get_all_users(db_session: Session) -> list[Type[User]]:
    return db_session.query(User).all()
