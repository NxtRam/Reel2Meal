"""
payment_service.py — Razorpay integration service layer.

Step 1: create_razorpay_order
  - Creates our Order row in DB (status=pending, payment_status=unpaid)
  - Calls Razorpay API to mint an order_id
  - Stores razorpay_order_id back on our row
  - Returns all data the frontend needs to open the checkout popup

Step 2: verify_payment
  - Re-computes HMAC-SHA256(order_id|payment_id, secret)
  - Raises 400 if signature doesn't match (tamper protection)
  - Updates Order: payment_status=paid, status=confirmed, payment_id stored
  - Returns success response
"""
import hashlib
import hmac
import uuid

import razorpay
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)

# Default price when no food item is linked: ₹299
DEFAULT_PRICE_INR = 299
CURRENCY = "INR"


def _razorpay_client() -> razorpay.Client:
    """Return a configured Razorpay client. Raises 503 if keys are missing/placeholder."""
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    if (
        not key_id
        or not key_secret
        or "PLACEHOLDER" in key_id
        or "PLACEHOLDER" in key_secret
        or key_id == "rzp_test_PLACEHOLDER"
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Razorpay is not configured. "
                "Add your RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to .env "
                "(get test keys at dashboard.razorpay.com → Settings → API Keys)."
            ),
        )
    return razorpay.Client(auth=(key_id, key_secret))


async def create_razorpay_order(
    db: AsyncSession,
    data: PaymentInitRequest,
    current_user: User,
) -> PaymentInitResponse:
    """
    Step 1 of checkout:
    1. Validate Razorpay keys are configured (raises 503 early if not)
    2. Determine amount (food item price × qty, or default ₹299)
    3. Create our Order row in DB
    4. Call Razorpay to get an order_id
    5. Persist razorpay_order_id on our row
    6. Return data for the frontend checkout popup
    """
    # ── Guard: validate keys exist before touching DB ───────────────────────────
    client = _razorpay_client()  # raises 503 if keys are missing/placeholder

    # ── Determine amount ──────────────────────────────────────────────────
    price_per_item_inr: float = DEFAULT_PRICE_INR

    if data.food_item_id:
        from app.models.food_item import FoodItem
        result = await db.execute(
            select(FoodItem).where(FoodItem.id == data.food_item_id)
        )
        food_item = result.scalar_one_or_none()
        if food_item and food_item.price:
            price_per_item_inr = float(food_item.price)

    if data.amount_paise:
        total_paise = data.amount_paise
        total_inr = total_paise / 100
    else:
        total_inr = price_per_item_inr * data.quantity
        total_paise = int(total_inr * 100)

    # ── Create our DB order ───────────────────────────────────────────────
    order = Order(
        user_id=current_user.id,
        reel_id=data.reel_id,
        food_item_id=data.food_item_id,
        restaurant_id=data.restaurant_id,
        quantity=data.quantity,
        note=data.note,
        total_price=total_inr,
        currency=CURRENCY,
        status=OrderStatus.pending,
        payment_status=PaymentStatus.unpaid,
    )
    db.add(order)
    await db.flush()          # Get order.id without committing yet

    # ── Call Razorpay ──────────────────────────────────────────────────
    rz_order = client.order.create({
        "amount": total_paise,
        "currency": CURRENCY,
        "receipt": str(order.id),
        "notes": {
            "reel_id": str(data.reel_id),
            "user_id": str(current_user.id),
        },
    })

    # ── Persist Razorpay order_id ────────────────────────────────────────────
    order.razorpay_order_id = rz_order["id"]
    await db.commit()
    await db.refresh(order)

    description = f"Reel2Meal order ×{data.quantity}"

    return PaymentInitResponse(
        our_order_id=order.id,
        razorpay_order_id=rz_order["id"],
        amount_paise=total_paise,
        currency=CURRENCY,
        key_id=settings.RAZORPAY_KEY_ID,
        description=description,
        prefill_name=current_user.username,
    )


async def verify_payment(
    db: AsyncSession,
    data: PaymentVerifyRequest,
    current_user: User,
) -> PaymentVerifyResponse:
    """
    Step 2 of checkout:
    1. Verify HMAC-SHA256 signature (tamper-proof, from Razorpay docs)
    2. Fetch our Order and confirm it belongs to this user
    3. Mark order as paid / confirmed
    """
    # ── Verify HMAC signature ─────────────────────────────────────────────────
    payload = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    expected_sig = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, data.razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment signature verification failed. Do not tamper with payment data.",
        )

    # ── Fetch our order ───────────────────────────────────────────────────────
    result = await db.execute(
        select(Order).where(
            Order.id == data.our_order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )
    if order.payment_status == PaymentStatus.paid:
        # Idempotent — already verified (e.g. double callback)
        return PaymentVerifyResponse(
            success=True,
            our_order_id=order.id,
            payment_status=PaymentStatus.paid,
            message="Payment already verified.",
        )

    # ── Mark paid ─────────────────────────────────────────────────────────────
    order.razorpay_payment_id = data.razorpay_payment_id
    order.payment_status = PaymentStatus.paid
    order.status = OrderStatus.confirmed
    await db.commit()

    return PaymentVerifyResponse(
        success=True,
        our_order_id=order.id,
        payment_status=PaymentStatus.paid,
        message="Payment successful! Your order is confirmed.",
    )


async def handle_payment_failure(
    db: AsyncSession,
    our_order_id: uuid.UUID,
    current_user: User,
) -> None:
    """Mark an order as failed when the user dismisses the Razorpay popup."""
    result = await db.execute(
        select(Order).where(
            Order.id == our_order_id,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if order and order.payment_status == PaymentStatus.unpaid:
        order.payment_status = PaymentStatus.failed
        order.status = OrderStatus.cancelled
        await db.commit()
