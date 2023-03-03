from dataclasses import dataclass
from typing import Any

from fastapi.requests import Request
from starlette_admin import RequestAction, BaseField
from starlette_admin.contrib.sqlmodel import ModelView

from app.models.users import User, Profile, Student, Teacher, Admin


@dataclass
class ProfileField(BaseField):
    multiple: bool = False
    render_function_key: str = "relation"
    form_template: str = "forms/relation.html"
    display_template: str = "displays/relation.html"
    identity: str = None

    async def serialize_value(
        self, request: Request, value: Any, action: RequestAction
    ) -> Any:
        self.identity = value.user.role
        return {"_detail_url": f"/admin/{value.user.role}/detail/{value.id}",
                "_edit_url": f"/admin/{value.user.role}/edit/{value.id}",
                "_repr": await self.repr(value, request),
                "id": value.id}

    @staticmethod
    async def repr(obj: Profile, request: Request):
        return "Profile"


class UserAdmin(ModelView):
    fields = ["id", "email", "role", ProfileField("profile")]
    exclude_fields_from_edit = ["profile"]

    async def repr(self, obj: User, request: Request) -> str:
        return f"{obj.id}: {obj.email}"


class StudentAdmin(ModelView):
    async def repr(self, obj: Student, request: Request) -> str:
        return f"{obj.id}: {obj.first_name} {obj.last_name}"


class TeacherAdmin(ModelView):
    async def repr(self, obj: Teacher, request: Request) -> str:
        return f"{obj.id}: {obj.first_name} {obj.last_name}"


class AdminAdmin(ModelView):
    async def repr(self, obj: Admin, request: Request) -> str:
        return f"{obj.id}: {obj.full_name}"
