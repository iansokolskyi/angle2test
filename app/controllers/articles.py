from typing import Type

from fastapi import HTTPException, UploadFile
from fastapi import status
from sqlmodel import select, Session
from sqlmodel.sql.expression import SelectOfScalar

from app.core.storage import LocalStorage
from app.models.articles import Article, ArticleCreate
from app.models.users import User, TeacherStudent, Student, Teacher


def get_article_by_id(article_id: int, session: Session) -> "Article":
    return session.query(Article).filter(Article.id == article_id).first()


def delete_article_by_id(article_id: int, session: Session) -> int:
    article = get_article_by_id(article_id, session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    session.delete(article)
    session.commit()
    return article_id


async def create_article(
    data: ArticleCreate,
    cover_image: UploadFile | None,
    session: Session,
) -> Article:
    article = Article(**data.dict())
    if cover_image and cover_image.size > 0:
        storage = LocalStorage()
        article.cover_image = storage.upload(cover_image)
        if cover_image.content_type not in ("image/png", "image/jpeg"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid image format",
            )

    session.add(article)
    session.commit()
    session.refresh(article)
    return article


def get_all_articles(session: Session) -> list[Type[Article]]:
    return session.query(Article).all()


def get_articles_by_author_id(
    author_id: int, session: Session
) -> list[Type[Article]]:
    return session.query(Article).filter(Article.author_id == author_id).all()


def get_student_articles_query(teacher_id: int) -> SelectOfScalar:
    return (
        select(Article)
        .join(Student, Article.author_id == Student.user_id)
        .join(TeacherStudent, Student.id == TeacherStudent.student_id)
        .join(Teacher, TeacherStudent.teacher_id == Teacher.id)
        .where(Teacher.user_id == teacher_id)
    )


def get_students_articles(teacher_id: int, session: Session) -> list[Type[Article]]:
    query = get_student_articles_query(teacher_id)
    return session.execute(query).scalars().all()


def get_student_article_by_id(
    teacher_id: int, article_id: int, session: Session
) -> Type[Article]:
    query = get_student_articles_query(teacher_id)
    query = query.filter(Article.id == article_id)
    return session.execute(query).scalars().first()


def get_own_article_by_id(
    article_id: int, user: User, session: Session
) -> "Article":
    return session.execute(
        select(Article)
        .where(Article.id == article_id, Article.author_id == user.id)
    ).scalars().first()


def delete_own_article_by_id(article_id: int, user: User, session: Session) -> int:
    article = get_own_article_by_id(article_id, user, session)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    session.delete(article)
    session.commit()
    return article_id
