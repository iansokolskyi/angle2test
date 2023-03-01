from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, Header
from fastapi.security import SecurityScopes
from sqlmodel import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.controllers.users import get_user_by_id
from core.db import engine

if TYPE_CHECKING:
    from models.users import User


def get_session():
    with Session(engine) as session:
        yield session


async def get_current_user(
    user_id=Header(None),
    session: Session = Depends(get_session),
    security_scopes: SecurityScopes = SecurityScopes(),
) -> "User":
    if user_id is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Provide valid user_id",
    )
    permissions_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="You don't have enough permissions",
    )
    if user_id is None:
        raise credentials_exception
    user = get_user_by_id(user_id, session)
    if user is None:
        raise credentials_exception
    if security_scopes.scopes:
        if user.role not in security_scopes.scopes:
            raise permissions_exception
    return user
