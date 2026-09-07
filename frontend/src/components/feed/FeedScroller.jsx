import { useState, useRef, useEffect } from 'react'
import ReelCard from './ReelCard'
import Spinner from '../shared/Spinner'
import { useFeed } from '../../hooks/useFeed'

/**
 * FeedScroller — Instagram Reels style vertical snap-scroll container.
 *
 * - CSS scroll-snap for native, zero-lag snapping
 * - IntersectionObserver (threshold 0.7) drives active reel tracking
 * - Pre-fetches next page when 2nd-to-last card is reached
 */
export default function FeedScroller() {
  const { reels, hasMore, loading, fetchFeed } = useFeed()
  const [activeIndex, setActiveIndex]  = useState(0)
  const [globalMuted, setGlobalMuted] = useState(true)
  const [globalMusicOn, setGlobalMusicOn] = useState(false)
  const containerRef  = useRef(null)
  const cardRefs      = useRef([])

  // ── Track visible reel ──────────────────────────────────────────────────
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const idx = cardRefs.current.indexOf(entry.target)
            if (idx !== -1) setActiveIndex(idx)
          }
        })
      },
      { root: container, threshold: 0.7 }
    )

    cardRefs.current.forEach((el) => el && observer.observe(el))
    return () => observer.disconnect()
  }, [reels.length])

  // ── Infinite scroll: load next page approaching end ─────────────────────
  useEffect(() => {
    if (activeIndex >= reels.length - 2 && hasMore && !loading) {
      fetchFeed()
    }
  }, [activeIndex, reels.length, hasMore, loading])

  // ── Loading / empty states ──────────────────────────────────────────────
  if (reels.length === 0 && loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-4 text-white">
        <Spinner size="lg" />
        <p className="text-white/50 text-sm">Loading reels…</p>
      </div>
    )
  }

  if (reels.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center gap-4 text-white/40">
        <span className="text-6xl">🎬</span>
        <p className="text-lg font-semibold">No reels yet</p>
        <p className="text-sm">Check back soon!</p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      id="feed-scroller"
      className="h-full overflow-y-scroll snap-y snap-mandatory"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      {/* Hide webkit scrollbar */}
      <style>{`#feed-scroller::-webkit-scrollbar { display: none; }`}</style>

      {reels.map((reel, i) => (
        <div
          key={reel.id}
          ref={(el) => (cardRefs.current[i] = el)}
          className="w-full snap-start snap-always"
          style={{ height: '100%', minHeight: '100%' }}
        >
          <ReelCard
            reel={reel}
            isActive={i === activeIndex}
            globalMuted={globalMuted}
            setGlobalMuted={setGlobalMuted}
            globalMusicOn={globalMusicOn}
            setGlobalMusicOn={setGlobalMusicOn}
          />
        </div>
      ))}

      {/* Loading next page */}
      {loading && (
        <div className="w-full h-20 flex items-center justify-center bg-black">
          <Spinner size="md" />
        </div>
      )}

      {/* End of feed */}
      {!hasMore && reels.length > 0 && (
        <div className="w-full h-20 flex items-center justify-center bg-black">
          <p className="text-white/30 text-sm">You've seen it all 🎉</p>
        </div>
      )}
    </div>
  )
}
