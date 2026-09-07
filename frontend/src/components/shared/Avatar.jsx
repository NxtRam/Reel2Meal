export default function Avatar({ src, name, size = 'md' }) {
  const sizes = { sm: 'w-7 h-7 text-xs', md: 'w-9 h-9 text-sm', lg: 'w-12 h-12 text-base' }

  return src ? (
    <img
      src={src}
      alt={name}
      className={`${sizes[size]} rounded-full object-cover ring-2 ring-white/20`}
    />
  ) : (
    <div
      className={`${sizes[size]} rounded-full gradient-bg flex items-center justify-center text-white font-bold flex-shrink-0`}
    >
      {name?.[0]?.toUpperCase() ?? '?'}
    </div>
  )
}
