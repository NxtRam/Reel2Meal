/**
 * Small restaurant badge at the top of the menu drawer.
 */
export default function RestaurantBadge({ restaurant }) {
  const mapsUrl = restaurant.latitude && restaurant.longitude
    ? `https://www.google.com/maps?q=${restaurant.latitude},${restaurant.longitude}`
    : `https://www.google.com/maps/search/${encodeURIComponent(restaurant.name + ' ' + (restaurant.city ?? ''))}`

  return (
    <a
      href={mapsUrl}
      target="_blank"
      rel="noopener noreferrer"
      id={`restaurant-badge-${restaurant.id}`}
      className="inline-flex items-center gap-2 glass px-3 py-1.5 rounded-full text-sm font-medium hover:bg-white/20 transition-all"
    >
      <span>📍</span>
      <span className="text-white/90">{restaurant.name}</span>
      {restaurant.city && (
        <span className="text-white/50">· {restaurant.city}</span>
      )}
    </a>
  )
}
