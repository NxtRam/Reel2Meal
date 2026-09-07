import pytest


@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "password123"
    })
    resp = await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "password123"
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(client):
    await client.post("/api/v1/auth/register", json={
        "username": "meuser",
        "email": "me@example.com",
        "password": "password123"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_restaurant(client):
    resp = await client.post("/api/v1/auth/register/restaurant", json={
        "username": "testrestaurant",
        "email": "restaurant@example.com",
        "password": "password123",
        "restaurant_name": "Test Pizza Place",
        "restaurant_address": "456 Pizza St",
        "restaurant_city": "Rome",
        "restaurant_contact": "1234567890"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testrestaurant"
    assert data["email"] == "restaurant@example.com"
    assert data["role"] == "restaurant"
    assert data["restaurant_id"] is not None
