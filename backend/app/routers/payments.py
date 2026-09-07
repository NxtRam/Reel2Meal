"""
routers/payments.py — Razorpay payment endpoints.

POST /api/v1/payments/create-order
  Creates a Razorpay order and returns the data needed to open
  the checkout popup on the frontend.

POST /api/v1/payments/verify
  Verifies the HMAC-SHA256 payment signature returned by Razorpay
  after the user completes payment. Marks the order as paid.

POST /api/v1/payments/{order_id}/failure
  Called when the user closes/cancels the Razorpay popup without paying.
  Marks the order as failed/cancelled so it doesn't linger as "pending".
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentInitRequest,
    PaymentInitResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from app.services import payment_service

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    redirect_slashes=False,
)


@router.post(
    "/create-order",
    response_model=PaymentInitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_order(
    data: PaymentInitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Step 1** of the checkout flow.

    Creates a Razorpay order and returns:
    - `razorpay_order_id` — passed to the Razorpay popup
    - `amount_paise` — amount in paise (₹1 = 100 paise)
    - `key_id` — Razorpay publishable key (safe for the frontend)
    - `our_order_id` — internal Order ID to send back during verification

    **Frontend usage:**
    ```js
    const rzp = new Razorpay({ key: key_id, order_id: razorpay_order_id, ... })
    rzp.open()
    ```
    """
    return await payment_service.create_razorpay_order(db, data, current_user)


@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(
    data: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Step 2** of the checkout flow.

    Called immediately after Razorpay's `payment.captured` callback fires.
    Verifies the cryptographic signature to confirm the payment is authentic,
    then marks the order as `paid` and `confirmed` in the database.

    Returns `success: true` on valid payment, `400` on signature mismatch.
    """
    return await payment_service.verify_payment(db, data, current_user)


@router.post("/{order_id}/failure", status_code=status.HTTP_204_NO_CONTENT)
async def report_payment_failure(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Called when the user dismisses the Razorpay popup without paying.
    Marks the pending order as `failed` / `cancelled` for clean bookkeeping.
    """
    await payment_service.handle_payment_failure(db, order_id, current_user)
