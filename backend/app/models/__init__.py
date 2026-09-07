# Import all models here so Alembic autogenerate can discover them
from app.models.user import User  # noqa: F401
from app.models.reel import Reel  # noqa: F401
from app.models.food_item import FoodItem  # noqa: F401
from app.models.restaurant import Restaurant, ReelRestaurant  # noqa: F401
from app.models.social import Like, Save, Comment  # noqa: F401
from app.models.order import Order  # noqa: F401
