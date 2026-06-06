from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "123456"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_login():
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()