import { Link } from 'react-router-dom'
import Avatar from '../shared/Avatar'
import OrderButton from './OrderButton'

/**
 * Bottom-left overlay: creator info, title, cuisine tag, and action CTAs.
 * Props:
 *   reel        – reel object
 *   onMenuOpen  – callback to open the menu drawer
 *   menuItems   – optional array of food items (forwarded to OrderButton)
 */
export default function ReelMeta({ reel, onMenuOpen, menuItems = [] }) {
  return (
    <div className="absolute bottom-0 left-0 right-16 p-4 pb-6 z-20">
      {/* Creator */}
      <Link
        to={`/u/${reel.creator.username}`}
        className="flex items-center gap-2 mb-2 w-fit"
        id={`reel-creator-${reel.id}`}
      >
        <Avatar src={reel.creator.avatar_url} name={reel.creator.username} size="sm" />
        <span className="text-white font-semibold text-sm drop-shadow">
          @{reel.creator.username}
        </span>
      </Link>

      {/* Title */}
      <p className="text-white font-bold text-base leading-snug drop-shadow mb-2 line-clamp-2">
        {reel.title}
      </p>

      {/* Cuisine tag */}
      {reel.cuisine_tag && (
        <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium gradient-bg text-white mb-3">
          {reel.cuisine_tag}
        </span>
      )}

      {/* CTA row: View Menu + Order Now */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* View Menu */}
        <button
          id={`reel-menu-btn-${reel.id}`}
          onClick={onMenuOpen}
          className="flex items-center gap-1.5 glass px-3 py-1.5 rounded-full text-sm font-medium text-white hover:bg-white/20 transition-all active:scale-95"
        >
          🍽️ <span>View Menu</span>
        </button>

        {/* Order Now */}
        <OrderButton reel={reel} menuItems={menuItems} />
      </div>
    </div>
  )
}
