"""
payment.py — Pydantic schemas for the Razorpay payment flow.

Flow:
  1. POST /payments/create-order  →  PaymentInitResponse
  2. Frontend opens Razorpay popup
  3. POST /payments/verify         →  PaymentVerifyResponse
"""
import uuid
from pydantic import BaseModel, Field


# ── 1. Create Razorpay order ─────────────────────────────────────────────────

class PaymentInitRequest(BaseModel):
    reel_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=99)
    food_item_id: uuid.UUID | None = None
    restaurant_id: uuid.UUID | None = None
    note: str | None = None
    # Optional price override (paise). If not set, backend calculates from food item
    # or falls back to a default of ₹299 per item.
    amount_paise: int | None = Field(default=None, ge=100)


class PaymentInitResponse(BaseModel):
    """Everything the frontend needs to open the Razorpay popup."""
    our_order_id: uuid.UUID       # Our internal Order.id
    razorpay_order_id: str        # Razorpay's order_XXXX
    amount_paise: int             # Amount in paise (₹1 = 100 paise)
    currency: str                 # "INR"
    key_id: str                   # Razorpay publishable key (safe to send to frontend)
    description: str              # e.g. "2x Neapolitan Pizza"
    prefill_name: str | None      # User's display name for Razorpay form


# ── 2. Verify payment signature ───────────────────────────────────────────────

class PaymentVerifyRequest(BaseModel):
    our_order_id: uuid.UUID          # Our internal Order.id
    razorpay_order_id: str           # From Razorpay callback
    razorpay_payment_id: str         # From Razorpay callback (pay_XXXX)
    razorpay_signature: str          # HMAC-SHA256 to verify


class PaymentVerifyResponse(BaseModel):
    success: bool
    our_order_id: uuid.UUID
    payment_status: str              # "paid" | "failed"
    message: str
