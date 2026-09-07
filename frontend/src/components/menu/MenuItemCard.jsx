/**
 * Individual food item card.
 * Shows image, name, description (2-line clamp), veg dot, and price.
 */
export default function MenuItemCard({ item }) {
  return (
    <div
      id={`menu-item-${item.id}`}
      className="flex gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
    >
      {/* Thumbnail */}
      {item.image_url ? (
        <img
          src={item.image_url}
          alt={item.name}
          className="w-20 h-20 rounded-lg object-cover flex-shrink-0 bg-surface-overlay"
        />
      ) : (
        <div className="w-20 h-20 rounded-lg bg-surface-overlay flex items-center justify-center flex-shrink-0 text-2xl">
          🍽️
        </div>
      )}

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 mb-0.5">
          {/* Veg/non-veg dot */}
          <span className={item.is_veg ? 'veg-dot mt-1' : 'nonveg-dot mt-1'} aria-label={item.is_veg ? 'Vegetarian' : 'Non-vegetarian'} />
          <h3 className="font-semibold text-white text-sm leading-snug">{item.name}</h3>
        </div>

        {item.description && (
          <p className="text-white/50 text-xs line-clamp-2 mb-1.5">{item.description}</p>
        )}

        {item.price != null && (
          <p className="text-brand-400 font-bold text-sm">
            {item.currency === 'INR' ? '₹' : item.currency} {Number(item.price).toLocaleString()}
          </p>
        )}
      </div>
    </div>
  )
}
