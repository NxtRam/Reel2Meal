import pytest
import uuid


@pytest.mark.asyncio
async def test_place_order_requires_auth(client):
    resp = await client.post("/api/v1/orders/", json={
        "reel_id": str(uuid.uuid4()),
        "quantity": 1,
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_orders_requires_auth(client):
    resp = await client.get("/api/v1/orders/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_order_reel_not_found(client):
    # Register + login
    await client.post("/api/v1/auth/register", json={
        "username": "orderuser",
        "email": "order@example.com",
        "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "order@example.com",
        "password": "password123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Place order on non-existent reel
    resp = await client.post(
        "/api/v1/orders/",
        json={"reel_id": str(uuid.uuid4()), "quantity": 2},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_orders_empty(client):
    await client.post("/api/v1/auth/register", json={
        "username": "orderlist",
        "email": "orderlist@example.com",
        "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "orderlist@example.com",
        "password": "password123",
    })
    token = login_resp.json()["access_token"]
    resp = await client.get("/api/v1/orders/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []
