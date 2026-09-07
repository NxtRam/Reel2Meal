import { create } from 'zustand'
import { reelsApi } from '../api/reelsApi'

export const useFeedStore = create((set, get) => ({
  reels: [],
  cursor: null,
  hasMore: true,
  loading: false,
  error: null,

  fetchFeed: async (reset = false) => {
    if (get().loading) return
    set({ loading: true, error: null })
    try {
      const params = { limit: 10 }
      if (!reset && get().cursor) params.cursor = get().cursor

      // Use public reels list when not on a specific feed
      const data = await reelsApi.list(params)

      set((state) => ({
        reels: reset ? data.data : [...state.reels, ...data.data],
        cursor: data.next_cursor,
        hasMore: data.has_more,
        loading: false,
      }))
    } catch (e) {
      set({ error: e.message, loading: false })
    }
  },

  // Optimistic like toggle
  toggleLike: async (reelId) => {
    set((state) => ({
      reels: state.reels.map((r) =>
        r.id === reelId
          ? { ...r, is_liked: !r.is_liked, like_count: r.is_liked ? r.like_count - 1 : r.like_count + 1 }
          : r
      ),
    }))
    try {
      const result = await reelsApi.like(reelId)
      set((state) => ({
        reels: state.reels.map((r) =>
          r.id === reelId ? { ...r, is_liked: result.liked, like_count: result.like_count } : r
        ),
      }))
    } catch {
      // Roll back on error
      set((state) => ({
        reels: state.reels.map((r) =>
          r.id === reelId
            ? { ...r, is_liked: !r.is_liked, like_count: r.is_liked ? r.like_count + 1 : r.like_count - 1 }
            : r
        ),
      }))
    }
  },

  // Optimistic save toggle
  toggleSave: async (reelId) => {
    set((state) => ({
      reels: state.reels.map((r) =>
        r.id === reelId ? { ...r, is_saved: !r.is_saved } : r
      ),
    }))
    try {
      await reelsApi.save(reelId)
    } catch {
      set((state) => ({
        reels: state.reels.map((r) =>
          r.id === reelId ? { ...r, is_saved: !r.is_saved } : r
        ),
      }))
    }
  },

  reset: () => set({ reels: [], cursor: null, hasMore: true, loading: false }),
}))
