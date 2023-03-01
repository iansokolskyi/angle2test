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
from sqlmodel import Session

from app.controllers.articles import (
    create_article,
    get_students_articles,
    get_student_article_by_id,
    get_own_article_by_id,
    delete_own_article_by_id,
    delete_article_by_id,
)
from app.controllers.articles import get_all_articles
from app.core.dependencies import get_session, get_current_user
from app.core.enums import Role
from app.models.articles import ArticleCreate, ArticleRead
from app.models.users import User

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def fetch_all_articles(
    user: User = Security(get_current_user, scopes=[Role.admin]),
    session: Session = Depends(get_session),
) -> list[ArticleRead]:
    articles = get_all_articles(session)
    return parse_obj_as(list[ArticleRead], articles)


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_article(
    cover_image: UploadFile | None = None,
    title: str = Form(...),
    content: str = Form(...),
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    session: Session = Depends(get_session),
) -> ArticleRead:
    article = await create_article(
        ArticleCreate(title=title, content=content, author_id=user.id),
        cover_image=cover_image,
        session=session,
    )
    return ArticleRead.from_orm(article)


@router.get("/own", status_code=status.HTTP_200_OK)
async def fetch_own_articles(
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    session: Session = Depends(get_session),
) -> list[ArticleRead]:
    articles = user.articles
    return parse_obj_as(list[ArticleRead], articles)


@router.get("/students", status_code=status.HTTP_200_OK)
async def fetch_student_articles(
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    session: Session = Depends(get_session),
) -> list[ArticleRead]:
    articles = get_students_articles(user.id, session)
    return parse_obj_as(list[ArticleRead], articles)


@router.get("/students/{article_id}", status_code=status.HTTP_200_OK)
async def fetch_student_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher]),
    session: Session = Depends(get_session),
) -> ArticleRead:
    article = get_student_article_by_id(user.id, article_id, session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleRead.from_orm(article)


@router.get("/own/{article_id}", status_code=status.HTTP_200_OK)
async def fetch_own_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    session: Session = Depends(get_session),
) -> ArticleRead:
    article = get_own_article_by_id(article_id, user, session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleRead.from_orm(article)


@router.delete("/own/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.teacher, Role.student]),
    session: Session = Depends(get_session),
) -> None:
    delete_own_article_by_id(article_id, user, session)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    user: User = Security(get_current_user, scopes=[Role.admin]),
    session: Session = Depends(get_session),
) -> None:
    delete_article_by_id(article_id, session)
