export default function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4 border-2', md: 'w-8 h-8 border-2', lg: 'w-12 h-12 border-3' }
  return (
    <div
      className={`${sizes[size]} ${className} rounded-full border-white/20 border-t-brand-500 animate-spin`}
      role="status"
      aria-label="Loading"
    />
  )
}
