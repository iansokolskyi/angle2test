from typing import Union

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.enums import Role
from app.models.users import User, profile_model_factory, UserCreate, UserRead


def get_user_by_id(user_id: int, session: Session) -> Union[User, None]:
    return session.get(User, user_id)


def get_user_by_email(email: str, session: Session) -> Union[User, None]:
    query = select(User).where(User.email == email)
    return session.exec(query).first()


def create_user(user: UserCreate, session: Session) -> UserRead:
    instance = select(User).where(User.email == user.email)
    if session.exec(instance).first():
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    password = user.dict().pop("password")

    db_user = User.from_orm(user)
    db_user.set_password(password)
    profile = profile_model_factory(user.role, user.profile, session)
    db_user.set_profile(profile)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    user = UserRead.from_orm(db_user)
    return user


def get_users_by_role(role: Role, session: Session) -> list[User]:
    query = select(User).where(User.role == role)
    return session.exec(query).all()


def get_all_users(session: Session) -> list[User]:
    return session.exec(select(User)).all()
