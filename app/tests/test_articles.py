import os
import tempfile

from fastapi import status

from app.core.storage import MEDIA_ROOT
from app.schemas.articles import ArticleSchema
from app.schemas.users import UserSchema
from .conftest import ADMIN_USER_ID, TEACHER_USER_ID


def test_fetch_all_articles(client):
    headers = {"user-id": ADMIN_USER_ID}
    response = client.get("/articles", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    articles = [ArticleSchema(**article) for article in response.json()]
    assert len(articles) > 0


def test_fetch_all_articles_fails_for_non_admin(client):
    headers = {"user-id": TEACHER_USER_ID}
    response = client.get("/articles", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_fetch_student_articles(client):
    headers = {"user-id": TEACHER_USER_ID}
    teacher_response = client.get("/users/profile", headers=headers)
    teacher = UserSchema(**teacher_response.json())

    response = client.get("/articles/students", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    articles = [ArticleSchema(**article) for article in response.json()]
    assert len(articles) > 0
    assert all(
        article.author.profile.teachers[0].last_name == teacher.profile.last_name
        for article in articles
    )


def test_fetch_student_article(client):
    headers = {"user-id": TEACHER_USER_ID}
    article_id = 1
    response = client.get(f"/articles/students/{article_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    article = ArticleSchema(**response.json())
    assert article.id == article_id


def test_fetch_own_articles(client):
    headers = {"user-id": TEACHER_USER_ID}
    teacher_response = client.get("/users/profile", headers=headers)
    teacher = UserSchema(**teacher_response.json())
    response = client.get("/articles/own", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    articles = [ArticleSchema(**article) for article in response.json()]
    assert len(articles) > 0
    assert all(
        article.author.profile.last_name == teacher.profile.last_name
        for article in articles
    )


def test_fetch_own_article(client):
    headers = {"user-id": TEACHER_USER_ID}
    articles_response = client.get("/articles/own", headers=headers)
    articles = [ArticleSchema(**article) for article in articles_response.json()]
    article_id = articles[0].id
    response = client.get(f"/articles/own/{article_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    article = ArticleSchema(**response.json())
    assert article.id == article_id


def test_create_article(client):
    headers = {"user-id": TEACHER_USER_ID}
    with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
        temp_file.write(b"test")
        temp_file.seek(0)

        article_data = {
            "title": "New Article",
            "content": "New Article Content"
        }
        response = client.post("/articles", data=article_data, files={'cover_image': temp_file},
                               headers=headers)
        os.remove(os.path.join(MEDIA_ROOT, os.path.basename(temp_file.name)))
    assert response.status_code == status.HTTP_201_CREATED
    article = ArticleSchema(**response.json())
    assert article.title == "New Article"
    assert article.content == "New Article Content"


def test_create_article_fails_with_wrong_file_type(client):
    headers = {"user-id": TEACHER_USER_ID}
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        temp_file.write(b"test")
        temp_file.seek(0)

        article_data = {
            "title": "New Article",
            "content": "New Article Content"
        }
        response = client.post(
            "/articles",
            data=article_data,
            files={'cover_image': temp_file},
            headers=headers
        )
        os.remove(os.path.join(MEDIA_ROOT, os.path.basename(temp_file.name)))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_article_fails_with_wrong_body(client):
    headers = {"user-id": TEACHER_USER_ID}
    article_data = {"title": "New Article", "content": ""}
    response = client.post("/articles", data=article_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_own_article(client):
    headers = {"user-id": TEACHER_USER_ID}
    articles_response = client.get("/articles/own", headers=headers)
    articles = [ArticleSchema(**article) for article in articles_response.json()]
    article_id = articles[0].id
    response = client.delete(f"/articles/own/{article_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/articles/own/{article_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_article(client):
    headers = {"user-id": ADMIN_USER_ID}
    article_id = 1
    response = client.delete(f"/articles/{article_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
