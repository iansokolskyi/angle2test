import datetime
from typing import Optional

from fastapi import UploadFile, File
from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship

from .users import UserRead, User


class ArticleBase(SQLModel):
    title: str = Field(max_length=100)
    cover_image: str | None = Field(max_length=256)
    content: str
    created_at: datetime.datetime = Field(default=datetime.datetime.now)


class Article(ArticleBase, table=True):
    __tablename__ = "articles"
    id: Optional[int] = Field(primary_key=True, index=True)
    author_id: Optional[int] = Field(foreign_key="users.id", nullable=False, index=True)
    author: Optional[User] = Relationship(back_populates="articles")

    def __repr__(self):
        return f"<{self.id}: {self.title}>"


class ArticleRead(ArticleBase):
    id: int
    author: UserRead


class ArticleCreate(ArticleBase):
    cover_image: UploadFile | None = File(default=None)
    author_id: int

    @validator("cover_image")
    def cover_image_must_be_image(cls, value):
        if value.content_type not in ["image/jpeg", "image/png"]:
            raise ValueError("Cover image must be a jpeg or png")
        return value

    @validator("title")
    def max_length(cls, value):
        if len(value) > 100:
            raise ValueError("Title must be less than 100 characters")
        return value
