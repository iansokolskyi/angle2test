from typing import Type

from fastapi import HTTPException, UploadFile
from fastapi import status
from sqlalchemy.orm import Session, Query

from app.core.storage import LocalStorage
from app.models.articles import Article
from app.models.users import User, Student, teacher_student, Teacher
from app.schemas.articles import ArticleCreateSchema


def get_article_by_id(article_id: int, db_session: Session) -> "Article":
    return db_session.query(Article).filter(Article.id == article_id).first()


def delete_article_by_id(article_id: int, db_session: Session) -> int:
    article = get_article_by_id(article_id, db_session)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db_session.delete(article)
    db_session.commit()
    return article_id


async def create_article(
    data: ArticleCreateSchema,
    user: User,
    cover_image: UploadFile | None,
    db_session: Session,
) -> Article:
    article = Article(**data.dict(), author_id=user.id)

    if cover_image and cover_image.size > 0:
        storage = LocalStorage()
        article.cover_image = storage.upload(cover_image)
        if cover_image.content_type not in ("image/png", "image/jpeg"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid image format",
            )

    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article


def get_all_articles(db_session: Session) -> list[Type[Article]]:
    return db_session.query(Article).all()


def get_articles_by_author_id(
    author_id: int, db_session: Session
) -> list[Type[Article]]:
    return db_session.query(Article).filter(Article.author_id == author_id).all()


def get_student_articles_query(teacher_id: int, db_session: Session) -> Query:
    return (
        db_session.query(Article)
        .join(Student, Article.author_id == Student.user_id)
        .join(teacher_student, Student.id == teacher_student.c.student_id)
        .join(Teacher, teacher_student.c.teacher_id == Teacher.id)
        .filter(Teacher.user_id == teacher_id)
    )


def get_students_articles(teacher_id: int, db_session: Session) -> list[Type[Article]]:
    query = get_student_articles_query(teacher_id, db_session)
    return query.all()


def get_student_article_by_id(
    teacher_id: int, article_id: int, db_session: Session
) -> Type[Article]:
    query = get_student_articles_query(teacher_id, db_session)
    return query.filter(Article.id == article_id).first()


def get_own_article_by_id(
    article_id: int, user: User, db_session: Session
) -> "Article":
    return (
        db_session.query(Article)
        .filter(Article.id == article_id, Article.author_id == user.id)
        .first()
    )


def delete_own_article_by_id(article_id: int, user: User, db_session: Session) -> int:
    article = get_own_article_by_id(article_id, user, db_session)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    db_session.delete(article)
    db_session.commit()
    return article_id
