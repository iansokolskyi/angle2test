from datetime import datetime

from fastapi import File, UploadFile
from pydantic import BaseModel, Field
from pydantic import validator

from app.schemas.users import UserSchema


class ArticleBaseSchema(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(..., min_length=1)
    cover_image: bytes | None = File(default=None)


class ArticleSchema(ArticleBaseSchema):
    id: int
    created_at: datetime
    author: UserSchema

    class Config:
        orm_mode = True


class ArticleCreateSchema(ArticleBaseSchema):
    cover_image: UploadFile | None = File(default=None)

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
