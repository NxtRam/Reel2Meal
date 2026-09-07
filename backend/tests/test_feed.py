import pytest


@pytest.mark.asyncio
async def test_feed_requires_auth(client):
    resp = await client.get("/api/v1/feed/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_reels_empty(client):
    resp = await client.get("/api/v1/reels/")
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert isinstance(body["data"], list)
    assert "has_more" in body


@pytest.mark.asyncio
async def test_list_reels_pagination_params(client):
    resp = await client.get("/api/v1/reels/?limit=5")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_reel_not_found(client):
    import uuid
    resp = await client.get(f"/api/v1/reels/{uuid.uuid4()}")
    assert resp.status_code == 404
