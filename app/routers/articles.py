from fastapi import (
    APIRouter,
    Depends,
    Security,
    HTTPException,
    status,
    UploadFile,
    Form,
)
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.controllers.articles import (
    create_article,
    get_students_articles,
    get_student_article_by_id,
    get_own_article_by_id,
    delete_own_article_by_id,
    delete_article_by_id,
)
from app.controllers.articles import get_all_articles
from app.core.dependencies import get_db, get_current_user
from app.core.enums import Role
from app.models.users import User
from app.schemas.articles import ArticleSchema, ArticleCreateSchema

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def fetch_all_articles(
    user: User = Security(get_current_user, scopes=[Role.admin]),
    db_session: Session = Depends(get_db),
) -> list[ArticleSchema]:
    articles = get_all_articles(db_session)
    return parse_obj_as(list[ArticleSchema], articles)


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_article(
    cover_image: UploadFile | None = None,
    title: str = Form(...),
    content: str = Form(...),
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    db_session: Session = Depends(get_db),
) -> ArticleSchema:
    article = await create_article(
        ArticleCreateSchema(title=title, content=content),
        user,
        cover_image=cover_image,
        db_session=db_session,
    )
    return ArticleSchema.from_orm(article)


@router.get("/own", status_code=status.HTTP_200_OK)
async def fetch_own_articles(
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    db_session: Session = Depends(get_db),
) -> list[ArticleSchema]:
    articles = user.articles
    return parse_obj_as(list[ArticleSchema], articles)


@router.get("/students", status_code=status.HTTP_200_OK)
async def fetch_student_articles(
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    db_session: Session = Depends(get_db),
) -> list[ArticleSchema]:
    articles = get_students_articles(user.id, db_session)
    return parse_obj_as(list[ArticleSchema], articles)


@router.get("/students/{article_id}", status_code=status.HTTP_200_OK)
async def fetch_student_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    db_session: Session = Depends(get_db),
) -> ArticleSchema:
    article = get_student_article_by_id(user.id, article_id, db_session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleSchema.from_orm(article)


@router.get("/own/{article_id}", status_code=status.HTTP_200_OK)
async def fetch_own_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    db_session: Session = Depends(get_db),
) -> ArticleSchema:
    article = get_own_article_by_id(article_id, user, db_session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleSchema.from_orm(article)


@router.delete("/own/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    db_session: Session = Depends(get_db),
) -> None:
    delete_own_article_by_id(article_id, user, db_session)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.admin]),
    db_session: Session = Depends(get_db),
) -> None:
    delete_article_by_id(article_id, db_session)
