from fastapi.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from app.models.articles import Article


class ArticleAdmin(ModelView):
    async def repr(self, obj: Article, request: Request) -> str:
        return obj.title
