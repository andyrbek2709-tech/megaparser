import pytest


async def _get_token(client) -> str:
    await client.post("/api/v1/auth/register", json={"email": "posts@example.com", "password": "password123"})
    res = await client.post("/api/v1/auth/login", json={"email": "posts@example.com", "password": "password123"})
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_list_posts_empty(client):
    token = await _get_token(client)
    response = await client.get("/api/v1/posts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
