from fastapi import APIRouter, Depends, Body, Security, status, Query
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.controllers.users import create_user, get_all_users, get_users_by_role
from app.core.dependencies import get_db, get_current_user
from app.core.enums import Role
from app.models.users import User
from app.schemas.users import (
    UserSchema,
    UserCreateSchema,
    StudentProfileSchema,
)

router = APIRouter()


@router.get("/profile", status_code=status.HTTP_200_OK)
async def fetch_own_profile(
    user: User = Depends(get_current_user), db_session: Session = Depends(get_db)
) -> UserSchema:
    return UserSchema.from_orm(user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreateSchema = Body(...), db_session: Session = Depends(get_db)
) -> UserSchema:
    user = create_user(user, db_session)
    return UserSchema.from_orm(user)


@router.get("", status_code=status.HTTP_200_OK)
async def fetch_all_users(
    user: User = Security(get_current_user, scopes=[Role.admin]),
    db_session: Session = Depends(get_db),
    role: Role | None = Query(None),
) -> list[UserSchema]:
    if role:
        users = get_users_by_role(role, db_session)
    else:
        users = get_all_users(db_session)
    return parse_obj_as(list[UserSchema], users)


@router.get("/students", response_model_exclude={"teachers"})
async def fetch_own_students(
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    db_session: Session = Depends(get_db),
) -> list[StudentProfileSchema]:
    return parse_obj_as(list[StudentProfileSchema], user.profile.students)
