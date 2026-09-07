import { useEffect } from 'react'
import { useFeedStore } from '../store/feedStore'

export function useFeed() {
  const { reels, hasMore, loading, fetchFeed, toggleLike, toggleSave, reset } = useFeedStore()

  // Load first page on mount
  useEffect(() => {
    if (reels.length === 0) fetchFeed(true)
    return () => reset()
  }, [])

  return { reels, hasMore, loading, fetchFeed, toggleLike, toggleSave }
}
