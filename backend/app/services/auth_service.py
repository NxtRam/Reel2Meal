from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.restaurant import Restaurant
from app.schemas.user import UserCreate, RestaurantRegisterRequest
from app.schemas.social import TokenOut
from app.utils.security import hash_password, verify_password, create_access_token


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    # Check uniqueness
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def register_restaurant(db: AsyncSession, data: RestaurantRegisterRequest) -> User:
    # Check uniqueness of user first
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )
        
    # Create the restaurant profile first
    restaurant = Restaurant(
        name=data.restaurant_name,
        address=data.restaurant_address,
        city=data.restaurant_city,
        contact=data.restaurant_contact,
    )
    db.add(restaurant)
    await db.flush() # Generate restaurant.id
    
    # Create the user account with role="restaurant" and link it
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="restaurant",
        restaurant_id=restaurant.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> TokenOut:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token, expires_in = create_access_token(str(user.id))
    return TokenOut(access_token=token, expires_in=expires_in)
