import { useState, useEffect } from 'react'
import { ordersApi } from '../api/ordersApi'
import { useAuth } from '../hooks/useAuth'
import Spinner from '../components/shared/Spinner'

// ─── Status helpers ───────────────────────────────────────────────────────────
const ORDER_STATUS = {
  confirmed: { label: 'Confirmed', color: 'text-green-400 bg-green-500/15 border-green-500/30', dot: 'bg-green-400', icon: '✅' },
  pending:   { label: 'Pending',   color: 'text-yellow-400 bg-yellow-500/15 border-yellow-500/30', dot: 'bg-yellow-400', icon: '⏳' },
  cancelled: { label: 'Cancelled', color: 'text-red-400 bg-red-500/15 border-red-500/30', dot: 'bg-red-400', icon: '❌' },
}

const PAYMENT_STATUS = {
  paid:    { label: 'Paid',    color: 'text-emerald-400 bg-emerald-500/10', icon: '💳' },
  unpaid:  { label: 'Unpaid',  color: 'text-yellow-400 bg-yellow-500/10',  icon: '🕐' },
  failed:  { label: 'Failed',  color: 'text-red-400 bg-red-500/10',        icon: '⚠️' },
}

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

// ─── Customer Order Card ──────────────────────────────────────────────────────
function CustomerOrderCard({ order, onCancel, cancelling }) {
  const os = ORDER_STATUS[order.status] ?? ORDER_STATUS.pending
  const ps = PAYMENT_STATUS[order.payment_status] ?? PAYMENT_STATUS.unpaid

  return (
    <div
      id={`order-card-${order.id}`}
      className="glass rounded-2xl overflow-hidden border border-white/8 hover:border-white/15 transition-all"
    >
      <div className={`h-0.5 w-full ${os.dot}`} />
      <div className="p-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <p className="text-white font-bold text-sm truncate">
              {os.icon} Order #{order.id.slice(0, 8).toUpperCase()}
            </p>
            <p className="text-white/40 text-xs mt-0.5">{timeAgo(order.created_at)}</p>
          </div>
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full border capitalize shrink-0 ${os.color}`}>
            {os.label}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-white/5 rounded-xl p-2.5">
            <p className="text-white/40 text-xs">Quantity</p>
            <p className="text-white font-bold text-lg leading-none mt-0.5">{order.quantity}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-2.5">
            <p className="text-white/40 text-xs">Total</p>
            <p className="text-brand-400 font-bold text-lg leading-none mt-0.5">
              {order.total_price ? `₹${Number(order.total_price).toLocaleString('en-IN')}` : '—'}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${ps.color}`}>
            {ps.icon} {ps.label}
          </span>
          {order.razorpay_payment_id && (
            <p className="text-white/25 text-xs font-mono truncate max-w-[120px]">
              {order.razorpay_payment_id}
            </p>
          )}
        </div>

        {order.note && (
          <p className="mt-2 text-white/40 text-xs italic border-t border-white/8 pt-2">
            "{order.note}"
          </p>
        )}

        {order.status === 'pending' && (
          <button
            id={`cancel-order-${order.id}`}
            onClick={() => onCancel(order.id)}
            disabled={cancelling === order.id}
            className="mt-3 w-full text-xs text-red-400 border border-red-500/30 px-3 py-1.5 rounded-full hover:bg-red-500/10 transition-colors disabled:opacity-50"
          >
            {cancelling === order.id ? 'Cancelling…' : '✕ Cancel Order'}
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Restaurant Incoming Order Card ──────────────────────────────────────────
function RestaurantOrderCard({ order, onUpdateStatus, updating }) {
  const os = ORDER_STATUS[order.status] ?? ORDER_STATUS.pending
  const ps = PAYMENT_STATUS[order.payment_status] ?? PAYMENT_STATUS.unpaid
  const isUpdating = updating === order.id

  return (
    <div
      id={`restaurant-order-card-${order.id}`}
      className="glass rounded-2xl overflow-hidden border border-white/8 hover:border-white/15 transition-all"
    >
      <div className={`h-0.5 w-full ${os.dot}`} />
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <p className="text-white font-bold text-sm truncate">
              {os.icon} Order #{order.id.slice(0, 8).toUpperCase()}
            </p>
            <p className="text-white/40 text-xs mt-0.5">{timeAgo(order.created_at)}</p>
          </div>
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full border capitalize shrink-0 ${os.color}`}>
            {os.label}
          </span>
        </div>

        {/* Price & Qty */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-white/5 rounded-xl p-2.5">
            <p className="text-white/40 text-xs">Qty</p>
            <p className="text-white font-bold text-lg leading-none mt-0.5">{order.quantity}</p>
          </div>
          <div className="bg-white/5 rounded-xl p-2.5">
            <p className="text-white/40 text-xs">Revenue</p>
            <p className="text-green-400 font-bold text-lg leading-none mt-0.5">
              {order.total_price ? `₹${Number(order.total_price).toLocaleString('en-IN')}` : '—'}
            </p>
          </div>
        </div>

        {/* Payment */}
        <div className="flex items-center gap-2 mb-3">
          <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${ps.color}`}>
            {ps.icon} {ps.label}
          </span>
        </div>

        {/* Customer note */}
        {order.note && (
          <p className="text-white/40 text-xs italic border border-white/8 rounded-lg px-3 py-2 mb-3">
            📝 "{order.note}"
          </p>
        )}

        {/* Action buttons — only show for pending orders */}
        {order.status === 'pending' && (
          <div className="flex gap-2 mt-1">
            <button
              id={`confirm-order-${order.id}`}
              onClick={() => onUpdateStatus(order.id, 'confirmed')}
              disabled={isUpdating}
              className="flex-1 text-xs font-semibold text-green-400 border border-green-500/30 px-3 py-2 rounded-xl hover:bg-green-500/10 transition-colors disabled:opacity-50"
            >
              {isUpdating ? '…' : '✅ Confirm'}
            </button>
            <button
              id={`reject-order-${order.id}`}
              onClick={() => onUpdateStatus(order.id, 'cancelled')}
              disabled={isUpdating}
              className="flex-1 text-xs font-semibold text-red-400 border border-red-500/30 px-3 py-2 rounded-xl hover:bg-red-500/10 transition-colors disabled:opacity-50"
            >
              {isUpdating ? '…' : '✕ Reject'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Summary bar ─────────────────────────────────────────────────────────────
function SummaryBar({ orders, isRestaurant }) {
  const confirmed = orders.filter((o) => o.status === 'confirmed')
  const revenue = confirmed.reduce((s, o) => s + (Number(o.total_price) || 0), 0)

  return (
    <div className="grid grid-cols-3 gap-3 mb-6">
      {[
        { label: 'Total Orders', value: orders.length, icon: isRestaurant ? '📦' : '🛒' },
        { label: isRestaurant ? 'Confirmed' : 'Confirmed', value: confirmed.length, icon: '✅' },
        {
          label: isRestaurant ? 'Total Revenue' : 'Total Spent',
          value: `₹${revenue.toLocaleString('en-IN')}`,
          icon: isRestaurant ? '💰' : '💸',
        },
      ].map(({ label, value, icon }) => (
        <div key={label} className="glass rounded-2xl p-3 text-center border border-white/8">
          <p className="text-lg">{icon}</p>
          <p className="text-white font-bold text-base leading-none mt-1">{value}</p>
          <p className="text-white/40 text-xs mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function OrdersPage() {
  const { user } = useAuth()
  const isRestaurant = user?.role === 'restaurant'

  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(null) // customer cancel
  const [updating, setUpdating] = useState(null)     // restaurant update status
  const [filter, setFilter] = useState('all')

  const load = () => {
    setLoading(true)
    const request = isRestaurant ? ordersApi.restaurantOrders() : ordersApi.list()
    request
      .then(setOrders)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => { if (user) load() }, [user])

  // Customer cancel
  const handleCancel = async (id) => {
    setCancelling(id)
    try {
      const updated = await ordersApi.cancel(id)
      setOrders((prev) => prev.map((o) => (o.id === id ? updated : o)))
    } catch (e) {
      alert(e.response?.data?.detail ?? 'Failed to cancel order.')
    } finally {
      setCancelling(null)
    }
  }

  // Restaurant confirm / reject
  const handleUpdateStatus = async (id, newStatus) => {
    setUpdating(id)
    try {
      const updated = await ordersApi.updateStatus(id, newStatus)
      setOrders((prev) => prev.map((o) => (o.id === id ? updated : o)))
    } catch (e) {
      alert(e.response?.data?.detail ?? 'Failed to update order status.')
    } finally {
      setUpdating(null)
    }
  }

  const FILTERS = ['all', 'pending', 'confirmed', 'cancelled']
  const filtered = filter === 'all' ? orders : orders.filter((o) => o.status === filter)

  const emptyMessage = isRestaurant
    ? 'No orders received yet'
    : 'No orders yet'
  const emptySubtext = isRestaurant
    ? 'Orders placed by customers will appear here.'
    : 'Tap "Order Now" on any reel to get started!'

  return (
    <div className="min-h-screen bg-surface pt-14 px-4">
      <div className="max-w-lg mx-auto py-8">

        {/* Title */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-2xl font-bold text-white">
              {isRestaurant ? '📦 Incoming Orders' : '🛒 Order History'}
            </h1>
            {isRestaurant && (
              <p className="text-white/40 text-xs mt-0.5">Customer orders for your restaurant</p>
            )}
          </div>
          {!loading && orders.length > 0 && (
            <button
              onClick={load}
              className="text-xs text-white/40 hover:text-white transition-colors"
            >
              ↺ Refresh
            </button>
          )}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-16">
            <Spinner size="lg" />
          </div>
        )}

        {/* Empty state */}
        {!loading && orders.length === 0 && (
          <div className="text-center py-20 text-white/40">
            <p className="text-6xl mb-4">{isRestaurant ? '📦' : '🛒'}</p>
            <p className="font-semibold text-white/60 text-lg">{emptyMessage}</p>
            <p className="text-sm mt-1">{emptySubtext}</p>
          </div>
        )}

        {/* Content */}
        {!loading && orders.length > 0 && (
          <>
            <SummaryBar orders={orders} isRestaurant={isRestaurant} />

            {/* Filter pills */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-1 scrollbar-hide">
              {FILTERS.map((f) => {
                const count = f === 'all' ? orders.length : orders.filter((o) => o.status === f).length
                return (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full border capitalize transition-all ${
                      filter === f
                        ? 'gradient-bg text-white border-transparent'
                        : 'text-white/50 border-white/15 hover:border-white/30'
                    }`}
                  >
                    {f === 'all' ? 'All' : f} ({count})
                  </button>
                )
              })}
            </div>

            {/* Order cards */}
            <div className="flex flex-col gap-3">
              {filtered.length === 0 ? (
                <p className="text-center text-white/30 text-sm py-8">No {filter} orders</p>
              ) : (
                filtered.map((order) =>
                  isRestaurant ? (
                    <RestaurantOrderCard
                      key={order.id}
                      order={order}
                      onUpdateStatus={handleUpdateStatus}
                      updating={updating}
                    />
                  ) : (
                    <CustomerOrderCard
                      key={order.id}
                      order={order}
                      onCancel={handleCancel}
                      cancelling={cancelling}
                    />
                  )
                )
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
