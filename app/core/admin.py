from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqlmodel import Admin as AdminApp

from app.admin.articles import ArticleAdmin
from app.admin.users import UserAdmin, TeacherAdmin, StudentAdmin, AdminAdmin
from app.models.articles import Article
from app.models.users import User, Admin, Student, Teacher
from core.auth import AdminAuthProvider
from core.db import engine

admin = AdminApp(engine, auth_provider=AdminAuthProvider(),
                 middlewares=[Middleware(SessionMiddleware, secret_key="secret")])
admin.add_view(
    DropDown(
        "Users",
        icon="fas fa-users",
        views=[
            UserAdmin(User),
            AdminAdmin(Admin),
            StudentAdmin(Student),
            TeacherAdmin(Teacher),
        ]
    )
)

admin.add_view(ArticleAdmin(Article))
