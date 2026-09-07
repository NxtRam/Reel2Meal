import { useState, useRef, useEffect, useCallback } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { commentsApi } from '../../api/commentsApi'
import Spinner from '../shared/Spinner'

/**
 * ChatDrawer — slide-up comments panel backed by the real DB.
 *
 * GET  /api/v1/reels/{reel_id}/comments  — loads on open
 * POST /api/v1/reels/{reel_id}/comments  — sends new comment
 *
 * Optimistic UI: comment appears instantly, rolls back on API error.
 */

const QUICK_REACTIONS = ['🔥', '😍', '😋', '👏', '❤️', '🤤']

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr)) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

// ── Single comment row ───────────────────────────────────────────────────────
function CommentRow({ c, onDelete, isOwn }) {
  return (
    <div className="flex gap-2.5 group animate-fade-in">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center text-xs font-bold text-white shrink-0 mt-0.5 select-none">
        {c.avatar_initial || c.username?.[0]?.toUpperCase() || '?'}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-1.5">
          <span className="text-white font-semibold text-xs">@{c.username || 'user'}</span>
          <span className="text-white/30 text-xs">{timeAgo(c.created_at)}</span>
        </div>
        <p className="text-white/85 text-sm mt-0.5 leading-relaxed break-words">{c.body}</p>
      </div>

      {/* Delete button — visible on hover for own comments */}
      {isOwn && (
        <button
          onClick={() => onDelete(c.id)}
          className="opacity-0 group-hover:opacity-100 transition-opacity text-white/20 hover:text-red-400 text-xs shrink-0 mt-1"
          aria-label="Delete comment"
        >
          ✕
        </button>
      )}
    </div>
  )
}

// ── Drawer ───────────────────────────────────────────────────────────────────
export default function ChatDrawer({ reel, open, onClose }) {
  const { isAuthenticated, user } = useAuth()
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(false)
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // ── Load comments when drawer opens ──────────────────────────────────────
  const loadComments = useCallback(async () => {
    if (!reel?.id) return
    setLoading(true)
    try {
      const data = await commentsApi.list(reel.id, 100)
      setComments(data)
    } catch (e) {
      console.error('Failed to load comments:', e)
    } finally {
      setLoading(false)
    }
  }, [reel?.id])

  useEffect(() => {
    if (open) {
      loadComments()
      setTimeout(() => inputRef.current?.focus(), 300)
    } else {
      setError('')
    }
  }, [open, loadComments])

  // Auto-scroll to bottom when new comments arrive
  useEffect(() => {
    if (open && comments.length > 0) {
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 80)
    }
  }, [comments.length, open])

  // ── Send a comment ────────────────────────────────────────────────────────
  const sendComment = async () => {
    const body = text.trim()
    if (!body || !isAuthenticated || sending) return
    setSending(true)
    setError('')

    // Optimistic add
    const optimistic = {
      id: `opt_${Date.now()}`,
      reel_id: reel.id,
      user_id: user?.id ?? '',
      body,
      created_at: new Date().toISOString(),
      username: user?.username ?? 'you',
      avatar_initial: user?.username?.[0]?.toUpperCase() ?? 'Y',
      _optimistic: true,
    }
    setComments((prev) => [...prev, optimistic])
    setText('')

    try {
      const saved = await commentsApi.create(reel.id, body)
      // Replace optimistic with real record
      setComments((prev) => prev.map((c) => (c.id === optimistic.id ? saved : c)))
    } catch (e) {
      // Roll back
      setComments((prev) => prev.filter((c) => c.id !== optimistic.id))
      setText(body) // restore text
      setError(e.response?.data?.detail ?? 'Failed to send. Please try again.')
    } finally {
      setSending(false)
    }
  }

  // ── Delete a comment ──────────────────────────────────────────────────────
  const deleteComment = async (commentId) => {
    // Optimistic remove
    setComments((prev) => prev.filter((c) => c.id !== commentId))
    try {
      await commentsApi.delete(reel.id, commentId)
    } catch (e) {
      // Restore on failure
      loadComments()
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendComment()
    }
  }

  const addReaction = (emoji) => {
    setText((t) => t + emoji)
    inputRef.current?.focus()
  }

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        id="chat-backdrop"
        className="fixed inset-0 bg-black/60 z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        id="chat-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Comments"
        className="fixed inset-x-0 bottom-0 z-[60] bg-surface-card rounded-t-3xl flex flex-col animate-slide-up shadow-2xl"
        style={{ maxHeight: '80vh' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-white/20" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 pb-3 border-b border-white/8">
          <div>
            <h2 className="font-bold text-white">
              💬 Comments
              {comments.length > 0 && (
                <span className="ml-2 text-white/40 text-sm font-normal">{comments.length}</span>
              )}
            </h2>
            <p className="text-white/40 text-xs mt-0.5 truncate max-w-[200px]">{reel?.title}</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full glass flex items-center justify-center text-white/50 hover:text-white text-sm"
          >
            ✕
          </button>
        </div>

        {/* Comments list */}
        <div className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4 scrollbar-hide">
          {loading ? (
            <div className="flex justify-center py-8">
              <Spinner size="lg" />
            </div>
          ) : comments.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-white/30">
              <p className="text-4xl mb-2">💬</p>
              <p className="text-sm font-medium">No comments yet</p>
              <p className="text-xs mt-1">Be the first to comment!</p>
            </div>
          ) : (
            comments.map((c) => (
              <CommentRow
                key={c.id}
                c={c}
                isOwn={c.user_id === user?.id}
                onDelete={deleteComment}
              />
            ))
          )}
          <div ref={bottomRef} />
        </div>

        {/* Quick reactions */}
        <div className="flex gap-2 px-5 py-2 border-t border-white/8">
          {QUICK_REACTIONS.map((emoji) => (
            <button
              key={emoji}
              onClick={() => addReaction(emoji)}
              className="text-xl hover:scale-125 transition-transform active:scale-95"
              aria-label={`React with ${emoji}`}
            >
              {emoji}
            </button>
          ))}
          {/* Character counter */}
          {text.length > 400 && (
            <span className={`ml-auto text-xs self-center ${text.length > 480 ? 'text-red-400' : 'text-white/40'}`}>
              {500 - text.length}
            </span>
          )}
        </div>

        {/* Error */}
        {error && (
          <p className="px-5 py-1 text-red-400 text-xs text-center animate-fade-in">{error}</p>
        )}

        {/* Input row */}
        <div className="flex items-center gap-2 px-4 py-3 border-t border-white/8" style={{ paddingBottom: 'max(12px, env(safe-area-inset-bottom))' }}>
          {/* Avatar */}
          <div className="w-7 h-7 rounded-full gradient-bg flex items-center justify-center text-xs font-bold text-white shrink-0">
            {isAuthenticated && user?.username ? user.username[0].toUpperCase() : '?'}
          </div>

          {isAuthenticated ? (
            <>
              <input
                ref={inputRef}
                id="chat-input"
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value.slice(0, 500))}
                onKeyDown={handleKey}
                placeholder="Add a comment…"
                className="flex-1 bg-surface-overlay border border-white/10 rounded-full px-4 py-2 text-white text-sm placeholder-white/30 focus:outline-none focus:border-brand-500 min-w-0"
                disabled={sending}
              />
              <button
                id="chat-send-btn"
                onClick={sendComment}
                disabled={!text.trim() || sending}
                className="w-9 h-9 gradient-bg rounded-full flex items-center justify-center shrink-0 disabled:opacity-40 hover:opacity-90 transition-opacity"
                aria-label="Send comment"
              >
                {sending ? <Spinner size="sm" /> : <span className="text-white text-sm font-bold">↑</span>}
              </button>
            </>
          ) : (
            <p className="flex-1 text-white/30 text-sm px-2">
              Sign in to leave a comment
            </p>
          )}
        </div>
      </div>
    </>
  )
}
