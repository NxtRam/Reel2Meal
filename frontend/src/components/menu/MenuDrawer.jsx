import { useEffect, useRef } from 'react'
import { useMenu } from '../../hooks/useMenu'
import MenuCategory from './MenuCategory'
import RestaurantBadge from './RestaurantBadge'
import Spinner from '../shared/Spinner'

/**
 * Bottom-sheet drawer that slides up with a spring animation.
 * Dismissed by clicking the backdrop or the × button.
 */
export default function MenuDrawer({ reelId, onClose, restaurants = [] }) {
  const { menu, loading, error } = useMenu(reelId)
  const drawerRef = useRef(null)

  // Prevent body scroll while open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  // Group items by category
  const grouped = {}
  if (menu) {
    menu.categories.forEach((cat) => {
      grouped[cat] = menu.items.filter((item) => (item.category ?? 'Other') === cat)
    })
  }

  return (
    <>
      {/* Backdrop */}
      <div
        id="menu-drawer-backdrop"
        onClick={onClose}
        className="fixed inset-0 bg-black/60 z-40 animate-fade-in"
      />

      {/* Drawer */}
      <div
        ref={drawerRef}
        id="menu-drawer"
        className="fixed bottom-0 left-0 right-0 z-50 bg-surface-card rounded-t-2xl max-h-[85vh] flex flex-col animate-slide-up"
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-white/20" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <h1 className="font-bold text-white text-lg">🍽️ Food Menu</h1>
          <button
            id="menu-drawer-close-btn"
            onClick={onClose}
            className="w-8 h-8 rounded-full glass flex items-center justify-center text-white/60 hover:text-white transition-colors"
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        {/* Restaurant badges */}
        {restaurants.length > 0 && (
          <div className="px-4 py-2 flex gap-2 flex-wrap border-b border-white/10">
            {restaurants.map((r) => (
              <RestaurantBadge key={r.id} restaurant={r} />
            ))}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto scrollbar-none pb-8">
          {loading && (
            <div className="flex items-center justify-center py-16">
              <Spinner size="lg" />
            </div>
          )}

          {error && (
            <div className="text-center py-16 text-white/40">
              <p className="text-3xl mb-2">😕</p>
              <p>Couldn't load the menu. Try again later.</p>
            </div>
          )}

          {menu && menu.items.length === 0 && (
            <div className="text-center py-16 text-white/40">
              <p className="text-3xl mb-2">📋</p>
              <p>No menu items yet.</p>
            </div>
          )}

          {menu && menu.categories.map((cat) => (
            <MenuCategory key={cat} category={cat} items={grouped[cat] ?? []} />
          ))}
        </div>
      </div>
    </>
  )
}
