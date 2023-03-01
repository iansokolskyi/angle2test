from fastapi import APIRouter, Depends, Body, Security, status, Query
from pydantic import parse_obj_as
from sqlmodel import Session

from app.controllers.users import create_user, get_all_users, get_users_by_role
from app.core.dependencies import get_current_user, get_session
from app.core.enums import Role
from app.models.users import User, UserCreate, Student, UserRead

router = APIRouter()


@router.get("/profile", status_code=status.HTTP_200_OK)
async def fetch_own_profile(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> UserRead:
    return UserRead.from_orm(user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate = Body(...), session: Session = Depends(get_session)
) -> UserRead:
    user = create_user(user, session)
    return user


@router.get("", status_code=status.HTTP_200_OK)
async def fetch_all_users(
    user: User = Security(get_current_user, scopes=[Role.admin]),
    session: Session = Depends(get_session),
    role: Role | None = Query(None),
) -> list[UserRead]:
    if role:
        users = get_users_by_role(role, session)
    else:
        users = get_all_users(session)
    return parse_obj_as(list[UserRead], users)


@router.get("/students", response_model_exclude={"teachers"})
async def fetch_own_students(
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    session: Session = Depends(get_session),
) -> list[Student]:
    return parse_obj_as(list[Student], user.profile.students)
