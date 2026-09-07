import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def place_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Place a new order from a reel.

    **Request body:**
    ```json
    {
      "reel_id": "uuid",
      "food_item_id": "uuid (optional)",
      "restaurant_id": "uuid (optional)",
      "quantity": 1,
      "note": "Extra spicy please"
    }
    ```
    Price is auto-calculated from the food item if provided.
    """
    return await order_service.place_order(db, data, current_user)


@router.get("/", response_model=list[OrderOut])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all orders for the authenticated user, newest first."""
    return await order_service.list_user_orders(db, current_user)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single order by ID (must belong to the authenticated user)."""
    return await order_service.get_order(db, order_id, current_user)


@router.post("/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a pending order. Returns 409 if already confirmed/cancelled."""
    return await order_service.cancel_order(db, order_id, current_user)


@router.get("/restaurant", response_model=list[OrderOut])
async def list_restaurant_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all incoming orders for the restaurant. Restaurant accounts only."""
    return await order_service.list_restaurant_orders(db, current_user)


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status of an order (confirm or cancel). Restaurant accounts only."""
    return await order_service.update_order_status(db, order_id, data.status, current_user)
