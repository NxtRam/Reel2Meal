from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, RestaurantRegisterRequest
from app.schemas.social import TokenOut, LoginRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, data)


@router.post("/register/restaurant", response_model=UserOut, status_code=201)
async def register_restaurant(data: RestaurantRegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_restaurant(db, data)


@router.post("/login", response_model=TokenOut)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login_user(db, data.email, data.password)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
