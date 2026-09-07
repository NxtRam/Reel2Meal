import axiosClient from './axiosClient'

/**
 * commentsApi.js — CRUD for reel comments.
 *
 * GET  /reels/{reelId}/comments       → list comments (public)
 * POST /reels/{reelId}/comments       → post new comment (auth required)
 * DELETE /reels/{reelId}/comments/{id} → delete own comment
 */
export const commentsApi = {
  /**
   * Fetch comments for a reel, chronological order.
   */
  list: (reelId, limit = 100) =>
    axiosClient
      .get(`/reels/${reelId}/comments/`, { params: { limit } })
      .then((r) => r.data),

  /**
   * Post a new comment.
   */
  create: (reelId, body) =>
    axiosClient
      .post(`/reels/${reelId}/comments/`, { body })
      .then((r) => r.data),

  /**
   * Delete own comment.
   */
  delete: (reelId, commentId) =>
    axiosClient.delete(`/reels/${reelId}/comments/${commentId}/`),
}
