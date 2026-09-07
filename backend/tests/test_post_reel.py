import pytest


@pytest.mark.asyncio
async def test_standard_user_cannot_create_reel(client):
    # 1. Register a standard user
    await client.post("/api/v1/auth/register", json={
        "username": "foodieuser",
        "email": "foodie@example.com",
        "password": "password123"
    })
    
    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "foodie@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    # 3. Try creating a reel
    resp = await client.post(
        "/api/v1/reels/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Unauthorised Reel",
            "video_url": "https://example.com/video.mp4"
        }
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Only restaurants can post reels"


@pytest.mark.asyncio
async def test_restaurant_can_create_reel_with_food_items(client):
    # 1. Register a restaurant
    await client.post("/api/v1/auth/register/restaurant", json={
        "username": "tastybites",
        "email": "tasty@example.com",
        "password": "password123",
        "restaurant_name": "Tasty Bites",
        "restaurant_address": "789 Gourmet Way",
        "restaurant_city": "Mumbai",
        "restaurant_contact": "9876543210"
    })
    
    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "tasty@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    
    # 3. Create a reel with food items
    resp = await client.post(
        "/api/v1/reels/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Sizzling Samosa 🥟",
            "description": "Watch how we prepare the crispest samosas!",
            "video_url": "https://example.com/samosa.mp4",
            "thumbnail_url": "https://example.com/samosa.jpg",
            "cuisine_tag": "Indian",
            "food_items": [
                {
                    "name": "Classic Veg Samosa",
                    "description": "Crispy pastry stuffed with spiced potato and peas.",
                    "price": 49.00,
                    "currency": "INR",
                    "category": "Starter",
                    "is_veg": True
                },
                {
                    "name": "Special Masala Chai",
                    "description": "Brewed with ginger, cardamom, and fresh milk.",
                    "price": 29.00,
                    "currency": "INR",
                    "category": "Drinks",
                    "is_veg": True
                }
            ]
        }
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Sizzling Samosa 🥟"
    assert data["creator"]["username"] == "tastybites"
    assert len(data["restaurants"]) == 1
    assert data["restaurants"][0]["name"] == "Tasty Bites"
    
    # 4. Fetch menu for this reel to verify food items are created & linked
    menu_resp = await client.get(f"/api/v1/menu/reel/{data['id']}")
    assert menu_resp.status_code == 200
    menu_data = menu_resp.json()
    assert len(menu_data["items"]) == 2
    
    names = [item["name"] for item in menu_data["items"]]
    assert "Classic Veg Samosa" in names
    assert "Special Masala Chai" in names

    samosa = next(item for item in menu_data["items"] if item["name"] == "Classic Veg Samosa")
    assert float(samosa["price"]) == 49.00

    chai = next(item for item in menu_data["items"] if item["name"] == "Special Masala Chai")
    assert float(chai["price"]) == 29.00
