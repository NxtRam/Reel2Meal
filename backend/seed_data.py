"""
Seed script — clears existing reels and populates with YouTube food shorts.
Run: python seed_data.py
"""
import asyncio
import uuid
from decimal import Decimal

from passlib.context import CryptContext
from sqlalchemy import text, delete, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

import os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sys.path.insert(0, str(Path(__file__).parent))
from app.database import Base
from app.models.user       import User
from app.models.restaurant import Restaurant, ReelRestaurant
from app.models.reel       import Reel
from app.models.food_item  import FoodItem
from app.models.social     import Like, Save
from app.models.order      import Order

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Restaurants ────────────────────────────────────────────────────────────────
RESTAURANTS = [
    {"name": "Spice Garden",    "address": "12 MG Road",        "city": "Bengaluru", "contact": "+91-9876543210", "lat": 12.9716, "lng": 77.5946},
    {"name": "The Biryani Hub", "address": "45 Jubilee Hills",   "city": "Hyderabad", "contact": "+91-9876543211", "lat": 17.4325, "lng": 78.4071},
    {"name": "Mumbai Tadka",    "address": "8 Linking Road",     "city": "Mumbai",    "contact": "+91-9876543212", "lat": 19.0596, "lng": 72.8295},
    {"name": "Punjab da Dhaba", "address": "22 Connaught Place", "city": "Delhi",     "contact": "+91-9876543213", "lat": 28.6315, "lng": 77.2167},
    {"name": "Chennai Delight", "address": "5 Anna Salai",       "city": "Chennai",   "contact": "+91-9876543214", "lat": 13.0827, "lng": 80.2707},
]

# ── Reels with real YouTube Shorts URLs ────────────────────────────────────────
REELS_DATA = [
    {
        "restaurant_idx": 1,
        "reel": {
            "title": "🍗 Hyderabadi Dum Biryani",
            "description": "Slow-cooked basmati rice with tender chicken, saffron, and traditional spices. Authentic Hyderabadi dum biryani!",
            "video_url": "https://www.youtube.com/shorts/z_5ql_YH2mQ",
            "thumbnail_url": "https://images.unsplash.com/photo-1563379091339-03246963d651?w=800",
            "duration_sec": 55,
            "cuisine_tag": "Biryani",
            "status": "published",
            "view_count": 3580,
            "like_count": 890,
        },
        "food_items": [
            {"name": "Chicken Dum Biryani", "description": "Slow-cooked chicken biryani with saffron & fried onions", "price": 350.00, "category": "Biryani",    "is_veg": False, "image_url": "https://images.unsplash.com/photo-1563379091339-03246963d651?w=400"},
            {"name": "Mutton Biryani",      "description": "Tender mutton pieces with aromatic basmati rice",          "price": 450.00, "category": "Biryani",    "is_veg": False, "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400"},
            {"name": "Mirchi Ka Salan",     "description": "Spicy green chilli curry — biryani's best companion",     "price": 80.00,  "category": "Side",       "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400"},
            {"name": "Raita",              "description": "Cool yogurt with cucumber and mint",                        "price": 60.00,  "category": "Side",       "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1571167530149-c1105da4c2c0?w=400"},
        ],
    },
    {
        "restaurant_idx": 3,
        "reel": {
            "title": "🥘 Butter Chicken & Dal Makhani Feast",
            "description": "The ultimate Punjabi combo — silky butter chicken paired with creamy slow-cooked black dal. Pure comfort!",
            "video_url": "https://www.youtube.com/shorts/Z_IbTzJ4rWU",
            "thumbnail_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800",
            "duration_sec": 50,
            "cuisine_tag": "North Indian",
            "status": "published",
            "view_count": 4200,
            "like_count": 1100,
        },
        "food_items": [
            {"name": "Butter Chicken",  "description": "Tender chicken in rich tomato-cream sauce",         "price": 320.00, "category": "Main Course", "is_veg": False, "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400"},
            {"name": "Dal Makhani",     "description": "Slow-cooked black lentils with butter and cream",    "price": 220.00, "category": "Main Course", "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400"},
            {"name": "Garlic Naan",     "description": "Naan bread topped with roasted garlic and coriander","price": 60.00,  "category": "Bread",       "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400"},
            {"name": "Lassi (Sweet)",   "description": "Thick creamy yogurt drink — mango or plain",         "price": 80.00,  "category": "Beverage",   "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1571167530149-c1105da4c2c0?w=400"},
        ],
    },
    {
        "restaurant_idx": 0,
        "reel": {
            "title": "🔥 Paneer Tikka Masala — Chef's Special",
            "description": "Creamy, smoky paneer tikka cooked in a rich tomato-based masala. A must-try vegetarian delight from North India!",
            "video_url": "https://www.youtube.com/shorts/x9hyKh5jOBs",
            "thumbnail_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800",
            "duration_sec": 45,
            "cuisine_tag": "North Indian",
            "status": "published",
            "view_count": 1240,
            "like_count": 312,
        },
        "food_items": [
            {"name": "Paneer Tikka Masala", "description": "Marinated paneer cubes in creamy tomato gravy",  "price": 280.00, "category": "Main Course", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400"},
            {"name": "Butter Naan",         "description": "Soft leavened bread brushed with butter",         "price": 50.00,  "category": "Bread",       "is_veg": True, "image_url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400"},
            {"name": "Jeera Rice",          "description": "Fragrant basmati rice tempered with cumin seeds", "price": 120.00, "category": "Rice",        "is_veg": True, "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400"},
        ],
    },
    {
        "restaurant_idx": 2,
        "reel": {
            "title": "🌮 Mumbai Street Style Pav Bhaji",
            "description": "Iconic Mumbai street food — spiced mashed vegetables served sizzling hot with loads of butter and soft pav!",
            "video_url": "https://www.youtube.com/shorts/ecHn4Dh8K_g",
            "thumbnail_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800",
            "duration_sec": 38,
            "cuisine_tag": "Street Food",
            "status": "published",
            "view_count": 2100,
            "like_count": 540,
        },
        "food_items": [
            {"name": "Pav Bhaji",       "description": "Spiced vegetable mash with 4 butter-toasted pavs",   "price": 150.00, "category": "Street Food", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400"},
            {"name": "Cheese Pav Bhaji","description": "Classic pav bhaji topped with generous extra cheese",  "price": 190.00, "category": "Street Food", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400"},
            {"name": "Vada Pav",        "description": "Spiced potato fritter in a bun — Mumbai's burger",    "price": 40.00,  "category": "Snack",       "is_veg": True, "image_url": "https://images.unsplash.com/photo-1606491955845-d9e8d99b0e44?w=400"},
            {"name": "Masala Chai",     "description": "Strong Indian spiced tea with ginger and cardamom",    "price": 30.00,  "category": "Beverage",   "is_veg": True, "image_url": "https://images.unsplash.com/photo-1517637382994-f02da38c6728?w=400"},
        ],
    },
    {
        "restaurant_idx": 4,
        "reel": {
            "title": "🦐 South Indian Prawn Ghee Roast",
            "description": "Juicy tiger prawns in a fiery Mangalorean ghee roast masala. Absolutely irresistible coastal South Indian flavours!",
            "video_url": "https://www.youtube.com/shorts/oppJG9jisus",
            "thumbnail_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800",
            "duration_sec": 50,
            "cuisine_tag": "South Indian",
            "status": "published",
            "view_count": 1890,
            "like_count": 430,
        },
        "food_items": [
            {"name": "Prawn Ghee Roast", "description": "Tiger prawns in Mangalorean spicy ghee masala",      "price": 420.00, "category": "Main Course", "is_veg": False, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=400"},
            {"name": "Appam (4 pcs)",    "description": "Soft fermented rice pancake with lacy crispy edges",  "price": 80.00,  "category": "Bread",       "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400"},
            {"name": "Fish Curry",       "description": "Traditional Chettinad fish curry with raw tamarind",  "price": 380.00, "category": "Main Course", "is_veg": False, "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400"},
            {"name": "Filter Coffee",    "description": "Strong South Indian drip coffee with frothy milk",     "price": 40.00,  "category": "Beverage",   "is_veg": True,  "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400"},
        ],
    },
    {
        "restaurant_idx": 0,
        "reel": {
            "title": "🍰 Gulab Jamun & Rasmalai Dessert Platter",
            "description": "Indulge in India's most loved sweets — soft gulab jamuns soaked in rose syrup paired with chilled creamy rasmalai!",
            "video_url": "https://www.youtube.com/shorts/uSV5C2YaAbw",
            "thumbnail_url": "https://images.unsplash.com/photo-1601050690117-94f5f7a74584?w=800",
            "duration_sec": 35,
            "cuisine_tag": "Dessert",
            "status": "published",
            "view_count": 2760,
            "like_count": 780,
        },
        "food_items": [
            {"name": "Gulab Jamun (6 pcs)", "description": "Soft milk-solid dumplings in rose-cardamom syrup",  "price": 120.00, "category": "Dessert", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1601050690117-94f5f7a74584?w=400"},
            {"name": "Rasmalai (4 pcs)",    "description": "Chilled cottage cheese discs in saffron cream",     "price": 150.00, "category": "Dessert", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1601050690117-94f5f7a74584?w=400"},
            {"name": "Kulfi Falooda",       "description": "Indian ice cream with rose syrup & basil seeds",    "price": 130.00, "category": "Dessert", "is_veg": True, "image_url": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=400"},
        ],
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created / verified")

    async with AsyncSessionLocal() as db:
        # ── Step 1: Delete all existing reel-related data ──────────────────────
        print("🗑️  Clearing old data...")
        await db.execute(delete(ReelRestaurant))
        await db.execute(delete(FoodItem))

        # Delete orders that reference reels
        from app.models.order import Order
        await db.execute(delete(Order))

        # Delete likes/saves
        await db.execute(delete(Like))
        await db.execute(delete(Save))

        # Delete reels
        await db.execute(delete(Reel))

        # Delete old restaurants and admin user (only seed-created ones)
        await db.execute(delete(Restaurant))
        result = await db.execute(select(User).where(User.email == "admin@reel2meal.com"))
        old_admin = result.scalar_one_or_none()
        if old_admin:
            await db.delete(old_admin)

        await db.flush()
        print("✅ Old data cleared")

        # ── Step 2: Create admin user ──────────────────────────────────────────
        owner = User(
            id=uuid.uuid4(),
            username="reel2meal_admin",
            email="admin@reel2meal.com",
            password_hash=pwd_ctx.hash("Admin@1234"),
            bio="Official Reel2Meal content team",
            role="restaurant",
        )
        db.add(owner)
        await db.flush()
        print(f"✅ Created user: {owner.username}")

        # ── Step 3: Create restaurants ─────────────────────────────────────────
        restaurant_objs = []
        for r in RESTAURANTS:
            rest = Restaurant(
                id=uuid.uuid4(),
                name=r["name"],
                address=r["address"],
                city=r["city"],
                contact=r["contact"],
                latitude=r["lat"],
                longitude=r["lng"],
            )
            db.add(rest)
            restaurant_objs.append(rest)
        await db.flush()
        print(f"✅ Created {len(restaurant_objs)} restaurants")

        # ── Step 4: Create reels + food items ─────────────────────────────────
        for entry in REELS_DATA:
            rest_obj = restaurant_objs[entry["restaurant_idx"]]
            reel = Reel(
                id=uuid.uuid4(),
                creator_id=owner.id,
                **entry["reel"],
            )
            db.add(reel)
            await db.flush()

            db.add(ReelRestaurant(reel_id=reel.id, restaurant_id=rest_obj.id))

            for fi in entry["food_items"]:
                db.add(FoodItem(
                    id=uuid.uuid4(),
                    reel_id=reel.id,
                    name=fi["name"],
                    description=fi["description"],
                    price=Decimal(str(fi["price"])),
                    currency="INR",
                    category=fi["category"],
                    is_veg=fi["is_veg"],
                    image_url=fi.get("image_url"),
                ))
            print(f"  🎬 {entry['reel']['title'][:55]}... ({len(entry['food_items'])} items)")

        await db.commit()
        print("\n🎉 Seeding complete!")
        print("   Login: admin@reel2meal.com / Admin@1234")
        print(f"   {len(REELS_DATA)} reels | {sum(len(e['food_items']) for e in REELS_DATA)} food items | {len(RESTAURANTS)} restaurants")


if __name__ == "__main__":
    asyncio.run(seed())
