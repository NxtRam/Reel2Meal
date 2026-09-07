"""
Seed script: inserts 55 YouTube food reels with food items into the DB.
Run from the backend/ directory:
    PYTHONPATH=. python app/utils/seed_reels.py
"""
import asyncio
import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select, text
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.reel import Reel
from app.models.food_item import FoodItem
from app.utils.security import hash_password

# ---------------------------------------------------------------------------
# Data: (title, yt_shorts_url, cuisine, description, [(item, price, veg)])
# ---------------------------------------------------------------------------
REELS = [
    ("🍕 Wood-Fired Margherita Magic", "https://youtube.com/shorts/1aym_5bE7Z8", "Italian",
     "Hand-stretched dough, San Marzano tomatoes, fresh buffalo mozzarella.",
     [("Margherita Pizza", 349, True), ("Garlic Bread", 99, True)]),

    ("🍜 Ramen in 30 Minutes", "https://youtube.com/shorts/keR7KUyQ2qQ", "Japanese",
     "Rich tonkotsu broth, soft-boiled egg, chashu pork.",
     [("Tonkotsu Ramen", 449, False), ("Gyoza (6 pcs)", 199, False)]),

    ("🥙 Street-Style Shawarma", "https://youtube.com/shorts/sMYyz3WeL18", "Middle Eastern",
     "Marinated chicken, garlic sauce, pickles wrapped in warm pita.",
     [("Chicken Shawarma", 199, False), ("Hummus Plate", 149, True)]),

    ("🍛 Butter Chicken Masterclass", "https://youtube.com/shorts/oeCIcV_QhHU", "Indian",
     "Creamy tomato gravy, tender chicken, served with naan.",
     [("Butter Chicken", 299, False), ("Butter Naan", 49, True), ("Jeera Rice", 99, True)]),

    ("🌮 Street Tacos Al Pastor", "https://youtube.com/shorts/EATsj7__fVw", "Mexican",
     "Spit-roasted pork, fresh pineapple, cilantro and onion.",
     [("Al Pastor Tacos (3)", 249, False), ("Churros", 129, True)]),

    ("🥩 Perfect Smash Burger", "https://youtube.com/shorts/OzmCRNRk9ME", "American",
     "Double smash patty, American cheese, secret sauce.",
     [("Smash Burger", 379, False), ("Loaded Fries", 179, True)]),

    ("🍣 Salmon Sushi Roll", "https://youtube.com/shorts/i5otDylcbY8", "Japanese",
     "Fresh salmon, avocado, cucumber, spicy mayo.",
     [("Salmon Roll (8 pcs)", 499, False), ("Miso Soup", 99, True)]),

    ("🍲 Chole Bhature Feast", "https://youtube.com/shorts/uDhhd4tY7KE", "Indian",
     "Spiced chickpeas, fluffy fried bread – a North Indian classic.",
     [("Chole Bhature (2 pcs)", 149, True), ("Lassi", 79, True)]),

    ("🧆 Crispy Falafel Bowl", "https://youtube.com/shorts/HIAB8zQoYDQ", "Middle Eastern",
     "Golden falafel, tahini, tabbouleh, warm pita.",
     [("Falafel Bowl", 249, True), ("Fattoush Salad", 149, True)]),

    ("🍝 Carbonara in 15 Minutes", "https://youtube.com/shorts/IUQvq2oRM1w", "Italian",
     "Guanciale, eggs, pecorino, fresh black pepper – authentic Roman style.",
     [("Spaghetti Carbonara", 399, False), ("Tiramisu", 199, True)]),

    ("🍗 Korean Fried Chicken", "https://youtube.com/shorts/3CBZI7QXIVQ", "Korean",
     "Double-fried crispy chicken tossed in gochujang glaze.",
     [("Korean Fried Chicken (6 pcs)", 349, False), ("Kimchi", 99, True)]),

    ("🥗 Poke Bowl Vibes", "https://youtube.com/shorts/4IgetiIp8Pk", "Hawaiian",
     "Ahi tuna, edamame, mango, sriracha mayo over sushi rice.",
     [("Tuna Poke Bowl", 449, False), ("Mochi Ice Cream", 149, True)]),

    ("🧀 4-Cheese Mac & Cheese", "https://youtube.com/shorts/OlpMLSpNjfI", "American",
     "Gruyère, cheddar, fontina, parmesan – baked golden on top.",
     [("4-Cheese Mac", 299, True), ("Coleslaw", 79, True)]),

    ("🫕 Biryani Dum Style", "https://youtube.com/shorts/M2mNc9I7IAE", "Indian",
     "Slow-cooked basmati, saffron, caramelised onions, whole spices.",
     [("Chicken Biryani", 349, False), ("Raita", 49, True), ("Salan", 79, True)]),

    ("🌯 Kathi Roll Supreme", "https://youtube.com/shorts/wvnXL_ycTXQ", "Indian",
     "Egg-coated paratha, seekh kebab, mint chutney.",
     [("Kathi Roll", 129, False), ("Masala Chai", 49, True)]),

    ("🍤 Crispy Tempura Prawns", "https://youtube.com/shorts/TVQWGGsSQoI", "Japanese",
     "Light batter, jumbo prawns, served with tentsuyu dipping sauce.",
     [("Prawn Tempura (4 pcs)", 399, False), ("Edamame", 149, True)]),

    ("🥘 Paneer Tikka Masala", "https://youtube.com/shorts/6wIjS64lrHM", "Indian",
     "Smoky marinated paneer in a rich tomato-cashew gravy.",
     [("Paneer Tikka Masala", 279, True), ("Garlic Naan", 59, True)]),

    ("🍔 Truffle Mushroom Burger", "https://youtube.com/shorts/8a41lbQ2JCU", "American",
     "Brioche bun, truffle aioli, portobello mushroom, Swiss cheese.",
     [("Truffle Mushroom Burger", 429, True), ("Sweet Potato Fries", 169, True)]),

    ("🦑 Spicy Squid Stir Fry", "https://youtube.com/shorts/O27nLt1BRa8", "Thai",
     "Wok-tossed squid, Thai basil, chilli, oyster sauce.",
     [("Thai Basil Squid", 349, False), ("Jasmine Rice", 79, True)]),

    ("🥐 French Croissant from Scratch", "https://youtube.com/shorts/Fkc7XBP8EiA", "French",
     "Laminated dough, 27 layers of butter, baked to golden perfection.",
     [("Butter Croissant", 129, True), ("Café au Lait", 149, True)]),

    ("🫔 Birria Tacos", "https://youtube.com/shorts/DcSSt27eGPE", "Mexican",
     "Slow-braised beef, consome for dipping, melted cheese.",
     [("Birria Tacos (3)", 349, False), ("Agua Fresca", 99, True)]),

    ("🍱 Bento Box Lunch", "https://youtube.com/shorts/uqAIsUowyCI", "Japanese",
     "Teriyaki chicken, tamagoyaki, edamame, pickled cucumber.",
     [("Teriyaki Bento", 399, False), ("Green Tea", 79, True)]),

    ("🥩 Slow-Roasted Ribs", "https://youtube.com/shorts/qZ-rT0A7MgM", "American",
     "Baby back ribs, smoky BBQ rub, 6 hours low & slow.",
     [("Full Rack BBQ Ribs", 849, False), ("Corn on Cob", 99, True)]),

    ("🍛 Hyderabadi Haleem", "https://youtube.com/shorts/VQ2CXvwuIPA", "Indian",
     "Slow-cooked wheat, lentils & mutton – 12 hour recipe.",
     [("Haleem Bowl", 249, False), ("Sheermal Bread", 49, False)]),

    ("🫙 Mango Lassi Bar", "https://youtube.com/shorts/AHopU8qMfNM", "Indian",
     "Alphonso mango, thick yoghurt, rose water.",
     [("Mango Lassi (large)", 99, True), ("Gulab Jamun (2)", 79, True)]),

    ("🍕 Detroit-Style Pizza", "https://youtube.com/shorts/m5cYzzHjjKA", "American",
     "Thick focaccia crust, Wisconsin brick cheese, pepperoni cups.",
     [("Detroit Pizza Slice", 299, False), ("Ranch Dip", 49, True)]),

    ("🥣 Açaí Bowl", "https://youtube.com/shorts/J6bSPGorLsA", "Brazilian",
     "Frozen açaí, banana, granola, honey, fresh berries.",
     [("Açaí Bowl", 299, True), ("Cold Brew", 149, True)]),

    ("🍜 Pad Thai Street Style", "https://youtube.com/shorts/gCr8DBywINw", "Thai",
     "Rice noodles, tamarind, peanuts, bean sprouts, lime.",
     [("Pad Thai (Chicken)", 279, False), ("Thai Iced Tea", 99, True)]),

    ("🍩 Gourmet Donuts", "https://youtube.com/shorts/c6WcA_UGHcQ", "American",
     "Brioche donuts, matcha glaze, strawberry cream, lotus crumble.",
     [("Donut Box (4 pcs)", 349, True), ("Cold Milk", 79, True)]),

    ("🧁 Brown Butter Cookies", "https://youtube.com/shorts/5CJFSY5HwYk", "Bakery",
     "Nutty brown butter, dark chocolate chunks, sea salt flakes.",
     [("Cookie Box (6 pcs)", 299, True), ("Espresso Shot", 99, True)]),

    ("🥙 Lebanese Manakish", "https://youtube.com/shorts/6Gl0y3IpyhY", "Middle Eastern",
     "Za'atar & olive oil flatbread baked in a stone oven.",
     [("Za'atar Manakish", 179, True), ("Mint Lemonade", 99, True)]),

    ("🍗 Chicken 65 Fry", "https://youtube.com/shorts/carsYXPsaUM", "Indian",
     "Deep-fried spiced chicken, curry leaves, green chilli tadka.",
     [("Chicken 65 (half)", 249, False), ("Onion Rings", 99, True)]),

    ("🦞 Lobster Bisque", "https://youtube.com/shorts/f4ucK6AUONg", "French",
     "Rich cream, cognac, fresh lobster meat, tarragon.",
     [("Lobster Bisque (bowl)", 699, False), ("Sourdough Bread", 99, True)]),

    ("🫕 Ethiopian Injera Feast", "https://youtube.com/shorts/qRRr00lgI2g", "Ethiopian",
     "Sourdough flatbread with doro wat, lentil misir, gomen.",
     [("Injera Combo Platter", 549, False), ("Ethiopian Coffee", 149, True)]),

    ("🍦 Soft Serve Perfection", "https://youtube.com/shorts/j6hv7Jcm5XQ", "Dessert",
     "Creamy vanilla soft serve, honeycomb crumble, caramel drizzle.",
     [("Soft Serve Cone", 129, True), ("Waffle Cup", 179, True)]),

    ("🥩 Wagyu Beef Steak", "https://youtube.com/shorts/lVfNStAU178", "Japanese",
     "A5 Wagyu, butter baste, served medium rare.",
     [("Wagyu Steak (150g)", 1499, False), ("Truffle Fries", 299, True)]),

    ("🫙 Overnight Oats 5 Ways", "https://youtube.com/shorts/TD-c7yRkEWI", "Healthy",
     "Chia, berries, peanut butter, mango, chocolate – meal prep.",
     [("Overnight Oat Jar", 149, True), ("Green Smoothie", 179, True)]),

    ("🥗 Caesar Salad Classic", "https://youtube.com/shorts/eK0sZELRsrY", "Italian",
     "Romaine, anchovy dressing, parmesan shavings, croutons.",
     [("Caesar Salad", 249, False), ("Iced Lemonade", 99, True)]),

    ("🍲 Rajma Chawal Comfort", "https://youtube.com/shorts/DqllbSMphXQ", "Indian",
     "Slow-cooked red kidney beans in spiced tomato masala.",
     [("Rajma Chawal", 149, True), ("Pickle & Papad", 39, True)]),

    ("🌮 Birria Quesabirria", "https://youtube.com/shorts/EQLhVOJedMw", "Mexican",
     "Cheesy braised beef quesadilla, dipped in rich consome.",
     [("Quesabirria (2 pcs)", 349, False), ("Horchata", 99, True)]),

    ("🍝 Truffle Pasta", "https://youtube.com/shorts/ehcVE5tIGS8", "Italian",
     "Fresh tagliatelle, black truffle, parmesan, butter sauce.",
     [("Truffle Tagliatelle", 599, True), ("Panna Cotta", 249, True)]),

    ("🥘 Daal Makhani Slow Cook", "https://youtube.com/shorts/JD6AChPiDss", "Indian",
     "Black lentils, rajma, butter, cream – 48 hour slow cooked.",
     [("Daal Makhani", 229, True), ("Stuffed Paratha", 89, True)]),

    ("🍗 Nashville Hot Chicken", "https://youtube.com/shorts/gZA5yW6Y-VI", "American",
     "Cayenne-laced fried chicken, pickle, white bread.",
     [("Nashville Hot Sandwich", 379, False), ("Buttermilk Ranch", 59, True)]),

    ("🥐 Shakshuka Brunch", "https://youtube.com/shorts/ni_HSCBqDlM", "Middle Eastern",
     "Poached eggs in spiced tomato pepper sauce, feta crumble.",
     [("Shakshuka (2 eggs)", 249, True), ("Pita Bread", 49, True)]),

    ("🍣 Temaki Hand Rolls", "https://youtube.com/shorts/0so5OhA6k7k", "Japanese",
     "Nori cone, sushi rice, tuna, avocado, sesame.",
     [("Temaki Set (3 pcs)", 449, False), ("Mochi Brownie", 199, True)]),

    ("🍜 Khao Soi Curry Noodles", "https://youtube.com/shorts/eqxk2rVPbdA", "Thai",
     "Coconut curry broth, egg noodles, crispy noodle nest.",
     [("Khao Soi (Chicken)", 329, False), ("Thai Basil Mocktail", 149, True)]),

    ("🥩 Grill Master Kebabs", "https://youtube.com/shorts/UXSsqiLCqkE", "Middle Eastern",
     "Seekh kebab, shish tawook, adana kebab combo platter.",
     [("Mixed Kebab Platter", 599, False), ("Hummus & Pita", 149, True)]),

    ("🫓 Sourdough from Starter", "https://youtube.com/shorts/zPxQjuFoUBc", "Bakery",
     "72-hour ferment, open crumb, shatteringly crisp crust.",
     [("Sourdough Loaf (400g)", 299, True), ("Cultured Butter", 99, True)]),

    ("🍦 Mango Kulfi on Stick", "https://youtube.com/shorts/UV5MmScWe0A", "Indian",
     "Alphonso mango, condensed milk, pistachio – frozen on stick.",
     [("Mango Kulfi", 79, True), ("Rose Sharbat", 59, True)]),

    ("🍔 Vada Pav Mumbai Style", "https://youtube.com/shorts/wUIoYL6IKT4", "Indian",
     "Spiced potato fritter, green chutney, tamarind, pav bun.",
     [("Vada Pav (2 pcs)", 59, True), ("Cutting Chai", 29, True)]),

    ("🦐 Prawn Malai Curry", "https://youtube.com/shorts/kQdasMB4bwc", "Indian",
     "Jumbo prawns in coconut cream, mustard seeds, turmeric.",
     [("Prawn Malai Curry", 399, False), ("Steamed Rice", 79, True)]),

    ("🍰 New York Cheesecake", "https://youtube.com/shorts/S_KPTWmP0HQ", "Dessert",
     "Dense cream cheese filling, graham cracker crust, berry compote.",
     [("NY Cheesecake Slice", 249, True), ("Filter Coffee", 99, True)]),

    ("🌶️ Chettinad Chicken Curry", "https://youtube.com/shorts/mqQDgm2qYQo", "Indian",
     "Black pepper, kalpasi, marathi mokku – fiery and aromatic.",
     [("Chettinad Chicken", 349, False), ("Appam (3 pcs)", 89, True)]),

    ("🥙 Döner Kebab Berlin Style", "https://youtube.com/shorts/wNao2A9I9yY", "Turkish",
     "Rotisserie lamb, garlic yoghurt, tomato, red cabbage, durum.",
     [("Döner Wrap", 279, False), ("Ayran Yoghurt Drink", 79, True)]),

    ("🍕 Neapolitan Diavola Pizza", "https://youtube.com/shorts/4Fo_Uybhtlc", "Italian",
     "San Marzano, fior di latte, spicy salami, chilli oil.",
     [("Diavola Pizza (12\")", 449, False), ("Burrata Starter", 299, True)]),
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Create or get seed restaurant user
        result = await db.execute(select(User).where(User.username == "reel2meal_kitchen"))
        seed_user = result.scalar_one_or_none()

        if not seed_user:
            # Create a seed restaurant
            rest = Restaurant(
                id=uuid.uuid4(),
                name="Reel2Meal Kitchen",
                address="42 Food Street, Mumbai",
                city="Mumbai",
                contact="9900000000",
            )
            db.add(rest)
            await db.flush()

            seed_user = User(
                id=uuid.uuid4(),
                username="reel2meal_kitchen",
                email="kitchen@reel2meal.app",
                password_hash=hash_password("kitchen@123"),
                role="restaurant",
                restaurant_id=rest.id,
                bio="Official Reel2Meal demo kitchen 🍽️",
            )
            db.add(seed_user)
            await db.flush()

        creator_id = seed_user.id

        # Delete existing seed reels to avoid duplicates on re-run
        await db.execute(text("DELETE FROM reels WHERE creator_id = :creator_id"), {"creator_id": creator_id})
        await db.flush()

        # Insert reels
        for i, (title, url, cuisine, desc, items) in enumerate(REELS):
            reel = Reel(
                id=uuid.uuid4(),
                creator_id=creator_id,
                title=title,
                description=desc,
                video_url=url,
                cuisine_tag=cuisine,
                status="published",
                like_count=10 + i * 7,
                view_count=100 + i * 23,
            )
            db.add(reel)
            await db.flush()

            for name, price, is_veg in items:
                fi = FoodItem(
                    id=uuid.uuid4(),
                    reel_id=reel.id,
                    name=name,
                    price=price,
                    currency="INR",
                    is_veg=is_veg,
                    category="Main" if not is_veg else "Veg",
                )
                db.add(fi)

        await db.commit()
        print(f"✅ Seeded {len(REELS)} reels with food items!")


if __name__ == "__main__":
    asyncio.run(seed())
