import pytest
import uuid


@pytest.mark.asyncio
async def test_menu_reel_not_found(client):
    resp = await client.get(f"/api/v1/menu/reel/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_food_item_not_found(client):
    resp = await client.get(f"/api/v1/menu/item/{uuid.uuid4()}")
    assert resp.status_code == 404
