import { useEffect, useRef } from 'react'

/**
 * Fires `callback` when the observed element enters the viewport.
 * @param {() => void} callback
 * @param {{ threshold?: number, rootMargin?: string }} options
 */
export function useIntersectionObserver(callback, { threshold = 0.8, rootMargin = '0px' } = {}) {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) callback()
      },
      { threshold, rootMargin }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [callback, threshold, rootMargin])

  return ref
}
