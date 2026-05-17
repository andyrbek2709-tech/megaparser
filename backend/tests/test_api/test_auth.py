import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "pass123"})
    response = await client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "pass123"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "password123"})
    response = await client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid(client):
    response = await client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_without_token(client):
    response = await client.get("/api/v1/posts")
    assert response.status_code == 403
