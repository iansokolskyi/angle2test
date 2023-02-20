from fastapi import Depends, HTTPException, Header
from fastapi.security import SecurityScopes
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.controllers.users import get_user_by_id
from app.core.db import DBSession
from app.schemas.users import UserSchema


def get_db():
    db_session = DBSession()
    try:
        yield db_session
    finally:
        db_session.close()


async def get_current_user(
    user_id=Header(None),
    db_session: Session = Depends(get_db),
    security_scopes: SecurityScopes = SecurityScopes(),
) -> UserSchema:
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
    user = get_user_by_id(user_id, db_session)
    if user is None:
        raise credentials_exception
    if security_scopes.scopes:
        if user.role not in security_scopes.scopes:
            raise permissions_exception
    return user
