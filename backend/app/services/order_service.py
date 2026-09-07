import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food_item import FoodItem
from app.models.order import Order
from app.models.reel import Reel
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate


async def place_order(db: AsyncSession, data: OrderCreate, user: User) -> OrderOut:
    """Create a new order linked to a reel (and optionally a food item)."""
    # Validate reel exists
    reel_result = await db.execute(
        select(Reel).where(Reel.id == data.reel_id, Reel.status == "published")
    )
    reel = reel_result.scalar_one_or_none()
    if not reel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found")

    # Optionally resolve price from the food item
    total_price = None
    currency = "INR"
    if data.food_item_id:
        fi_result = await db.execute(
            select(FoodItem).where(
                FoodItem.id == data.food_item_id,
                FoodItem.reel_id == data.reel_id,
            )
        )
        food_item = fi_result.scalar_one_or_none()
        if not food_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found on this reel",
            )
        if food_item.price is not None:
            total_price = float(food_item.price) * data.quantity
            currency = food_item.currency

    order = Order(
        user_id=user.id,
        reel_id=data.reel_id,
        food_item_id=data.food_item_id,
        restaurant_id=data.restaurant_id,
        quantity=data.quantity,
        note=data.note,
        total_price=total_price,
        currency=currency,
        status="pending",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return OrderOut.model_validate(order)


async def list_user_orders(db: AsyncSession, user: User) -> list[OrderOut]:
    """Return all orders for the authenticated user, newest first."""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )
    return [OrderOut.model_validate(o) for o in result.scalars().all()]


async def get_order(db: AsyncSession, order_id: uuid.UUID, user: User) -> OrderOut:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderOut.model_validate(order)


async def cancel_order(db: AsyncSession, order_id: uuid.UUID, user: User) -> OrderOut:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel an order with status '{order.status}'",
        )
    order.status = "cancelled"
    await db.commit()
    await db.refresh(order)
    return OrderOut.model_validate(order)


async def list_restaurant_orders(db: AsyncSession, user: User) -> list[OrderOut]:
    """Return all orders received by the restaurant the user belongs to."""
    if not user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not linked to a restaurant",
        )
    result = await db.execute(
        select(Order)
        .where(Order.restaurant_id == user.restaurant_id)
        .order_by(Order.created_at.desc())
    )
    return [OrderOut.model_validate(o) for o in result.scalars().all()]


async def update_order_status(
    db: AsyncSession, order_id: uuid.UUID, new_status: str, user: User
) -> OrderOut:
    """Allow a restaurant to update the status of an incoming order."""
    if not user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant accounts can update order status",
        )
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.restaurant_id == user.restaurant_id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or does not belong to your restaurant",
        )
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return OrderOut.model_validate(order)
