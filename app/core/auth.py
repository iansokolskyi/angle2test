from fastapi.requests import Request
from fastapi.responses import Response
from sqlmodel import Session
from starlette_admin.auth import AuthProvider as BaseAuthProvider
from starlette_admin.exceptions import LoginFailed

from app.controllers.users import get_user_by_email
from app.models.users import User
from core.db import engine


class AdminAuthProvider(BaseAuthProvider):
    async def login(self,
                    username: str,
                    password: str,
                    remember_me: bool,
                    request: Request,
                    response: Response,
                    ) -> Response:
        with Session(engine) as session:
            user = get_user_by_email(username, session)
            if user:
                if not user.check_password(password):
                    raise LoginFailed(msg="Invalid username or password")
                if not user.is_staff:
                    raise LoginFailed(msg="You are not allowed to access admin panel")
                else:
                    request.session.update({"user": user.dict()})
                    return response

    @staticmethod
    async def get_user_from_session(request: Request) -> User | None:
        session_user = request.session.get("user")
        if session_user:
            user = User(**session_user)
            return user

    async def is_authenticated(self, request) -> bool:
        user = await self.get_user_from_session(request)
        if not user or not user.is_staff:
            return False
        request.state.user = user
        return True

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
