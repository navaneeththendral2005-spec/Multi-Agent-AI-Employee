import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_student():
    response = client.post(
        "/students",
        json={"name": "John Doe", "email": "john@example.com", "age": 20, "grade": "A"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["age"] == 20
    assert data["grade"] == "A"
    assert "id" in data


def test_create_student_duplicate_email():
    student_data = {"name": "John Doe", "email": "john@example.com", "age": 20, "grade": "A"}
    client.post("/students", json=student_data)
    response = client.post("/students", json=student_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Student with this email already exists"


def test_read_students():
    client.post("/students", json={"name": "Alice", "email": "alice@example.com", "age": 21, "grade": "B"})
    client.post("/students", json={"name": "Bob", "email": "bob@example.com", "age": 22, "grade": "A"})

    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_student_by_id():
    create_response = client.post(
        "/students",
        json={"name": "Alice", "email": "alice@example.com", "age": 21, "grade": "B"}
    )
    student_id = create_response.json()["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"


def test_read_student_not_found():
    response = client.get("/students/999")
    assert response.status_code == 404


def test_update_student():
    create_response = client.post(
        "/students",
        json={"name": "Alice", "email": "alice@example.com", "age": 21, "grade": "B"}
    )
    student_id = create_response.json()["id"]

    response = client.put(
        f"/students/{student_id}",
        json={"name": "Alice Smith", "age": 22}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["age"] == 22
    assert data["email"] == "alice@example.com"


def test_delete_student():
    create_response = client.post(
        "/students",
        json={"name": "Alice", "email": "alice@example.com", "age": 21, "grade": "B"}
    )
    student_id = create_response.json()["id"]

    delete_response = client.delete(f"/students/{student_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/students/{student_id}")
    assert get_response.status_code == 404