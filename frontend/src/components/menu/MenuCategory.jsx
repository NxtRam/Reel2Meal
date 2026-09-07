import MenuItemCard from './MenuItemCard'

/**
 * A grouped section of food items under a category heading.
 */
export default function MenuCategory({ category, items }) {
  return (
    <div>
      <div className="sticky top-0 bg-surface-card/90 backdrop-blur z-10 px-4 py-2">
        <h2 className="text-xs font-bold uppercase tracking-widest text-brand-400">
          {category}
        </h2>
      </div>
      <div className="px-2">
        {items.map((item) => (
          <MenuItemCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  )
}
