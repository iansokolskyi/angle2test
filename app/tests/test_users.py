from fastapi import status

from app.models.users import UserRead, Student
from .conftest import ADMIN_USER_ID, TEACHER_USER_ID


def test_get_own_profile(client):
    headers = {"user-id": ADMIN_USER_ID}
    response = client.get("/users/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    user = UserRead(**response.json())
    assert user.email == "admin@test.com"
    assert user.profile.full_name is not None


def test_fetch_all_users(client):
    # Test successful response with no role specified
    headers = {"user-id": ADMIN_USER_ID}
    response = client.get("/users", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 2

    # Test successful response with role filter
    headers = {"user-id": ADMIN_USER_ID}
    params = {"role": "student"}
    response = client.get("/users", params=params, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_fetch_all_users_fails_for_non_admin(client):
    headers = {"user-id": TEACHER_USER_ID}
    response = client.get("/users", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_register_admin(client):
    user_data = {
        "email": "newadmin@example.com",
        "password": "password1",
        "role": "admin",
        "profile": {"full_name": "New Admin"},
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    user = UserRead(**response.json())
    assert user.email == "newadmin@example.com"


def test_register_user_with_existing_email_fails(client):
    user_data = {
        "email": "admin@test.com",
        "password": "password1",
        "role": "admin",
        "profile": {"full_name": "New Admin"},
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 400


def test_register_user_with_simple_password_fails(client):
    user_data = {
        "email": "newadmin@test.com",
        "password": "pass",
        "role": "admin",
        "profile": {"full_name": "New Admin"},
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_teacher(client):
    user_data = {
        "email": "newteacher@test.com",
        "password": "password1",
        "role": "teacher",
        "profile": {"first_name": "New", "last_name": "Teacher", "degree": "Bachelor"},
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    user = UserRead(**response.json())
    assert user.email == "newteacher@test.com"
    assert user.profile.degree == "Bachelor"


def test_register_student(client):
    user_data = {
        "email": "newstudent@test.com",
        "password": "password1",
        "role": "student",
        "profile": {
            "first_name": "New",
            "last_name": "Student",
            "teachers": [1],
            "entry_date": "2021-01-01",
        },
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    user = UserRead(**response.json())
    assert user.email == "newstudent@test.com"
    assert len(user.profile.teachers) > 0


def test_register_student_with_no_teachers_fails(client):
    user_data = {
        "email": "newstudent@test.com",
        "password": "password1",
        "role": "student",
        "profile": {
            "first_name": "New",
            "last_name": "Student",
            "teachers": [],
            "entry_date": "2021-01-01",
        },
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_register_student_with_invalid_entry_date_fails(client):
    user_data = {
        "email": "newstudent@test.com",
        "password": "password1",
        "role": "student",
        "profile": {
            "first_name": "New",
            "last_name": "Student",
            "teachers": [1],
            "entry_date": "2024-01-01",
        },
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_fetch_associated_students(client):
    headers = {"user-id": TEACHER_USER_ID}
    response = client.get("/users/students", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    students = [Student(**student) for student in response.json()]
    assert len(students) > 0
    assert students[0].last_name == "Student1"
