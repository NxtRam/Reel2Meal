import { useState } from 'react'
import { paymentApi } from '../../api/paymentApi'
import { useAuth } from '../../hooks/useAuth'
import { useRazorpay } from '../../hooks/useRazorpay'
import Spinner from '../shared/Spinner'

// ── Static delivery partner pool (randomised per order) ──────────────────────
const DELIVERY_PARTNERS = [
  { name: 'Rajesh Kumar',  mobile: '98765 43210', avatar: '👨' },
  { name: 'Priya Sharma',  mobile: '87654 32109', avatar: '👩' },
  { name: 'Amir Khan',     mobile: '76543 21098', avatar: '🧑' },
  { name: 'Sneha Patil',   mobile: '65432 10987', avatar: '👩‍🦱' },
  { name: 'Vikram Singh',  mobile: '99988 77665', avatar: '👨‍🦱' },
]

function randomPartner() {
  return DELIVERY_PARTNERS[Math.floor(Math.random() * DELIVERY_PARTNERS.length)]
}

function randomDeliveryTime() {
  // Random between 20–45 mins
  return Math.floor(Math.random() * 26) + 20
}

// ── Checkout Step Component (Swiggy-style) ───────────────────────────────────
function CheckoutStep({ totalDisplay, onConfirm, onBack }) {
  const [address, setAddress] = useState('')
  const [addressType, setAddressType] = useState('Home')
  const [floor, setFloor] = useState('')
  const [landmark, setLandmark] = useState('')
  const [error, setError] = useState('')

  const [partner] = useState(() => randomPartner())
  const [deliveryMins] = useState(() => randomDeliveryTime())
  const [arrivalTime] = useState(() => {
    const t = new Date(Date.now() + randomDeliveryTime() * 60 * 1000)
    return t.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
  })

  const handleConfirm = () => {
    if (!address.trim()) {
      setError('Please enter your delivery address.')
      return
    }
    onConfirm({ address, addressType, floor, landmark })
  }

  return (
    <div className="flex flex-col gap-0 max-h-[75vh] overflow-y-auto scrollbar-none">
      {/* Back + title */}
      <div className="flex items-center gap-3 mb-4 sticky top-0 bg-surface-card pt-1 pb-2 z-10">
        <button onClick={onBack} className="w-7 h-7 rounded-full glass flex items-center justify-center text-white/60 hover:text-white text-sm shrink-0">
          ←
        </button>
        <h2 className="font-bold text-white text-base">Delivery Details</h2>
      </div>

      {/* ── Delivery ETA banner ────────────────────────────────────── */}
      <div className="bg-gradient-to-r from-brand-600/30 to-brand-500/10 border border-brand-500/25 rounded-2xl p-4 mb-4 flex items-center gap-3">
        <span className="text-3xl">🛵</span>
        <div>
          <p className="text-white font-bold text-sm">Delivery in {deliveryMins} mins</p>
          <p className="text-white/50 text-xs mt-0.5">Estimated arrival by {arrivalTime}</p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-brand-400 font-bold text-lg">₹{totalDisplay}</p>
          <p className="text-white/40 text-xs">to pay</p>
        </div>
      </div>

      {/* ── Delivery Partner card ──────────────────────────────────── */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-4 mb-4">
        <p className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">Delivery Partner</p>
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center text-2xl shrink-0">
            {partner.avatar}
          </div>
          <div className="flex-1">
            <p className="text-white font-semibold text-sm">{partner.name}</p>
            <p className="text-white/40 text-xs mt-0.5">📞 {partner.mobile}</p>
          </div>
          <a
            href={`tel:${partner.mobile.replace(/\s/g, '')}`}
            className="w-9 h-9 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center text-green-400 text-base hover:bg-green-500/30 transition-colors"
            aria-label="Call delivery partner"
            onClick={(e) => e.stopPropagation()}
          >
            📞
          </a>
        </div>

        {/* Live tracker bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-white/40 mb-1.5">
            <span>Order Placed</span>
            <span>Preparing</span>
            <span>On the way</span>
            <span>Delivered</span>
          </div>
          <div className="relative h-1.5 bg-white/10 rounded-full">
            <div className="h-full w-[30%] bg-brand-500 rounded-full" />
            <div className="absolute top-1/2 left-[28%] -translate-y-1/2 w-3.5 h-3.5 bg-brand-500 rounded-full border-2 border-black flex items-center justify-center">
              <span className="text-[6px]">🛵</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Address input ──────────────────────────────────────────── */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-4 mb-4 flex flex-col gap-3">
        <p className="text-xs font-semibold text-white/40 uppercase tracking-wider">Delivery Address</p>

        {/* Address type selector */}
        <div className="flex gap-2">
          {['Home', 'Work', 'Other'].map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setAddressType(type)}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                addressType === type
                  ? 'gradient-bg text-white border-transparent'
                  : 'text-white/50 border-white/15 hover:border-white/30'
              }`}
            >
              {type === 'Home' ? '🏠' : type === 'Work' ? '💼' : '📍'} {type}
            </button>
          ))}
        </div>

        {/* Full address */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-white/50">Full Address *</label>
          <textarea
            id="checkout-address"
            value={address}
            onChange={(e) => { setAddress(e.target.value); setError('') }}
            placeholder="House/Flat no., Building name, Street, Area…"
            rows={2}
            className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white text-sm placeholder-white/30 focus:outline-none focus:border-brand-500 resize-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-white/50">Floor / Wing</label>
            <input
              type="text"
              value={floor}
              onChange={(e) => setFloor(e.target.value)}
              placeholder="e.g. 3rd Floor, B Wing"
              className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white text-xs placeholder-white/30 focus:outline-none focus:border-brand-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-white/50">Landmark</label>
            <input
              type="text"
              value={landmark}
              onChange={(e) => setLandmark(e.target.value)}
              placeholder="Near Metro / Mall…"
              className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white text-xs placeholder-white/30 focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>
      </div>

      {/* ── Fare breakdown ─────────────────────────────────────────── */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-4 mb-4">
        <p className="text-xs font-semibold text-white/40 uppercase tracking-wider mb-3">Bill Summary</p>
        <div className="flex flex-col gap-2 text-sm">
          <div className="flex justify-between text-white/70">
            <span>Item Total</span>
            <span>₹{totalDisplay}</span>
          </div>
          <div className="flex justify-between text-white/70">
            <span>Delivery Fee</span>
            <span className="text-green-400">FREE</span>
          </div>
          <div className="flex justify-between text-white/50 text-xs">
            <span>GST & Charges</span>
            <span>₹0</span>
          </div>
          <div className="border-t border-white/10 pt-2 flex justify-between font-bold text-white">
            <span>To Pay</span>
            <span className="text-brand-400">₹{totalDisplay}</span>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <p className="text-red-400 text-xs text-center bg-red-500/10 rounded-lg px-3 py-2 mb-3">
          {error}
        </p>
      )}

      {/* CTA */}
      <button
        id="checkout-proceed-to-pay"
        onClick={handleConfirm}
        className="gradient-bg text-white font-bold py-3.5 rounded-xl hover:opacity-90 active:scale-95 transition-all flex items-center justify-center gap-2 text-sm"
      >
        <span>💳</span>
        <span>Proceed to Pay ₹{totalDisplay}</span>
      </button>

      <p className="text-white/25 text-xs text-center mt-2 mb-1">
        UPI · Cards · Net Banking · Wallets — secured by Razorpay 🔒
      </p>
    </div>
  )
}

// ── Main OrderButton ─────────────────────────────────────────────────────────
/**
 * OrderButton — \"Order Now\" button with Swiggy-style checkout flow.
 *
 * Flow:
 *   1. User clicks \"Order Now\" → order modal opens (item/qty/note)
 *   2. User clicks \"Proceed\" → Checkout step (address + delivery partner)
 *   3. User clicks \"Pay\" → Razorpay popup
 *   4. On success → backend verifies → order confirmed ✅
 */
export default function OrderButton({ reel, menuItems = [], onSuccess }) {
  const { isAuthenticated } = useAuth()
  const { ready: rzpReady, openCheckout } = useRazorpay()

  const [open, setOpen] = useState(false)
  const [step, setStep] = useState('order')      // 'order' | 'checkout'
  const [selectedItem, setSelectedItem] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(false)
  const [paymentStep, setPaymentStep] = useState('idle')
  const [error, setError] = useState('')
  const [paidOrder, setPaidOrder] = useState(null)

  const unitPrice = selectedItem?.price ? Number(selectedItem.price) : 299
  const totalInr = unitPrice * quantity
  const totalDisplay = totalInr.toLocaleString('en-IN')

  const handleOpen = () => {
    if (!isAuthenticated) {
      setError('Please sign in to place an order.')
      setTimeout(() => setError(''), 3000)
      return
    }
    setOpen(true)
    setStep('order')
    setPaymentStep('idle')
    setError('')
  }

  const handleClose = () => {
    if (loading) return
    setOpen(false)
    setSelectedItem(null)
    setQuantity(1)
    setNote('')
    setError('')
    setPaymentStep('idle')
    setPaidOrder(null)
    setStep('order')
  }

  const handleProceedToCheckout = () => {
    setStep('checkout')
    setError('')
  }

  const handlePay = async (deliveryInfo) => {
    setLoading(true)
    setError('')
    setPaymentStep('creating')

    let orderData
    try {
      orderData = await paymentApi.createOrder({
        reel_id: reel.id,
        food_item_id: selectedItem?.id ?? null,
        quantity,
        note: [
          note || null,
          deliveryInfo ? `Deliver to: ${deliveryInfo.addressType} — ${deliveryInfo.address}${deliveryInfo.floor ? ', ' + deliveryInfo.floor : ''}${deliveryInfo.landmark ? ' (Near: ' + deliveryInfo.landmark + ')' : ''}` : null
        ].filter(Boolean).join(' | ') || null,
      })
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Could not initiate payment. Please try again.')
      setPaymentStep('idle')
      setLoading(false)
      return
    }

    setPaymentStep('idle')

    openCheckout({
      key: orderData.key_id,
      order_id: orderData.razorpay_order_id,
      amount: orderData.amount_paise,
      currency: orderData.currency,
      name: 'Reel2Meal',
      description: orderData.description,
      image: 'https://i.imgur.com/n5tjHFD.png',
      prefill: { name: orderData.prefill_name ?? '' },
      theme: { color: '#ff6b35' },
      handler: async (response) => {
        setLoading(true)
        setPaymentStep('verifying')
        try {
          const result = await paymentApi.verifyPayment({
            our_order_id: orderData.our_order_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          })
          setPaidOrder(result)
          setPaymentStep('success')
          onSuccess?.(result)
          setTimeout(handleClose, 2500)
        } catch {
          setError('Payment verification failed. Contact support with your payment ID.')
          setPaymentStep('failed')
        } finally {
          setLoading(false)
        }
      },
      modal: {
        ondismiss: () => {
          paymentApi.reportFailure(orderData.our_order_id)
          setPaymentStep('failed')
          setError('Payment was cancelled. You can try again.')
          setLoading(false)
        },
      },
    })
  }

  return (
    <>
      {/* Trigger button */}
      <button
        id={`order-btn-${reel.id}`}
        onClick={handleOpen}
        className="flex items-center gap-1.5 px-4 py-2 rounded-full gradient-bg text-white font-semibold text-sm shadow-lg hover:opacity-90 active:scale-95 transition-all"
        aria-label="Order from this reel"
      >
        🛒 <span>Order Now</span>
      </button>

      {error && !open && (
        <p className="mt-1 text-red-400 text-xs animate-fade-in">{error}</p>
      )}

      {open && (
        <>
          {/* Backdrop */}
          <div
            id="order-modal-backdrop"
            className="fixed inset-0 bg-black/70 z-50 animate-fade-in"
            onClick={handleClose}
          />

          {/* Dialog */}
          <div
            id="order-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Place your order"
            className="fixed inset-x-4 bottom-8 z-[60] bg-surface-card rounded-2xl p-5 animate-slide-up max-w-sm mx-auto shadow-2xl"
          >
            {/* ── SUCCESS STATE ──────────────────────────────────────── */}
            {paymentStep === 'success' ? (
              <div className="flex flex-col items-center py-6 gap-3 animate-fade-in">
                <span className="text-5xl">🎉</span>
                <p className="font-bold text-white text-lg">Payment Successful!</p>
                <p className="text-white/50 text-sm text-center">
                  Your order is confirmed. Our delivery partner is on the way! 🛵
                </p>
                {paidOrder?.our_order_id && (
                  <p className="text-xs text-white/30 font-mono">
                    Order #{String(paidOrder.our_order_id).slice(0, 8).toUpperCase()}
                  </p>
                )}
              </div>

            ) : paymentStep === 'verifying' ? (
              <div className="flex flex-col items-center py-8 gap-3 animate-fade-in">
                <Spinner size="lg" />
                <p className="text-white/70 text-sm">Verifying payment…</p>
              </div>

            ) : step === 'checkout' ? (
              /* ── CHECKOUT STEP (address + delivery partner) ──────── */
              <CheckoutStep
                totalDisplay={totalDisplay}
                onConfirm={handlePay}
                onBack={() => setStep('order')}
              />

            ) : (
              /* ── ORDER FORM ───────────────────────────────────────── */
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-bold text-white text-lg">🛒 Place Order</h2>
                  <button
                    type="button"
                    id="order-modal-close"
                    onClick={handleClose}
                    className="w-7 h-7 rounded-full glass flex items-center justify-center text-white/50 hover:text-white text-sm"
                  >
                    ✕
                  </button>
                </div>

                <p className="text-white/60 text-sm line-clamp-1">
                  From: <span className="text-white font-medium">{reel.title}</span>
                </p>

                {/* Item selector */}
                {menuItems.length > 0 && (
                  <div className="flex flex-col gap-1.5">
                    <label htmlFor="order-item-select" className="text-xs font-semibold uppercase tracking-widest text-white/50">
                      Select Item
                    </label>
                    <select
                      id="order-item-select"
                      value={selectedItem?.id ?? ''}
                      onChange={(e) => {
                        const found = menuItems.find((m) => m.id === e.target.value)
                        setSelectedItem(found ?? null)
                      }}
                      className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-brand-500"
                    >
                      <option value="">— Full Reel Order (₹299) —</option>
                      {menuItems.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                          {item.price ? ` — ₹${Number(item.price).toLocaleString('en-IN')}` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Quantity + live total */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="order-quantity" className="text-xs font-semibold uppercase tracking-widest text-white/50">
                    Quantity
                  </label>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      id="order-qty-minus"
                      onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                      className="w-9 h-9 rounded-full glass flex items-center justify-center text-white text-lg font-bold hover:bg-white/20 transition-colors"
                    >
                      −
                    </button>
                    <span id="order-quantity" className="text-white font-bold text-xl min-w-[2rem] text-center">
                      {quantity}
                    </span>
                    <button
                      type="button"
                      id="order-qty-plus"
                      onClick={() => setQuantity((q) => Math.min(99, q + 1))}
                      className="w-9 h-9 rounded-full glass flex items-center justify-center text-white text-lg font-bold hover:bg-white/20 transition-colors"
                    >
                      +
                    </button>
                    <span className="ml-auto text-brand-400 font-bold text-lg">₹{totalDisplay}</span>
                  </div>
                </div>

                {/* Note */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="order-note" className="text-xs font-semibold uppercase tracking-widest text-white/50">
                    Special Instructions
                  </label>
                  <textarea
                    id="order-note"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="Extra spicy, no onions…"
                    rows={2}
                    className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white text-sm placeholder-white/30 focus:outline-none focus:border-brand-500 resize-none"
                  />
                </div>

                {error && (
                  <div className="text-red-400 text-sm bg-red-500/10 rounded-lg px-3 py-2 text-center">
                    <p>{error}</p>
                    {paymentStep === 'failed' && (
                      <button onClick={() => { setError(''); setPaymentStep('idle') }} className="mt-1 text-xs text-white/50 underline">
                        Try again
                      </button>
                    )}
                  </div>
                )}

                {/* Proceed → Checkout button */}
                <button
                  id="order-proceed-btn"
                  type="button"
                  onClick={handleProceedToCheckout}
                  disabled={loading || !rzpReady}
                  className="gradient-bg text-white font-bold py-3 rounded-xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {!rzpReady ? (
                    <span className="text-sm">Loading payment gateway…</span>
                  ) : (
                    <>
                      <span>📍</span>
                      <span>Add Delivery Address →</span>
                    </>
                  )}
                </button>

                <p className="text-white/30 text-xs text-center">
                  Next: Add delivery address & confirm
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </>
  )
}
