import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useFeedStore } from '../../store/feedStore'
import ChatDrawer from './ChatDrawer'

function ActionButton({ id, icon, label, onClick, className = '' }) {
  const [pop, setPop] = useState(false)

  const handleClick = () => {
    setPop(true)
    setTimeout(() => setPop(false), 300)
    onClick?.()
  }

  return (
    <button
      id={id}
      onClick={handleClick}
      className={`action-btn text-white ${className}`}
      aria-label={label}
    >
      <span className={`text-3xl transition-transform ${pop ? 'animate-pop' : ''}`}>
        {icon}
      </span>
      {label && <span className="text-xs font-medium text-white/80 drop-shadow">{label}</span>}
    </button>
  )
}

/**
 * Right-rail action buttons: like, save, chat, share.
 * Chat now opens a slide-up ChatDrawer.
 */
export default function ReelActions({ reel }) {
  const { isAuthenticated } = useAuth()
  const { toggleLike, toggleSave } = useFeedStore()
  const [chatOpen, setChatOpen] = useState(false)

  const handleLike = () => {
    if (!isAuthenticated) return
    toggleLike(reel.id)
  }

  const handleSave = () => {
    if (!isAuthenticated) return
    toggleSave(reel.id)
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({ title: reel.title, url: window.location.href })
    } else {
      navigator.clipboard.writeText(window.location.href)
    }
  }

  return (
    <>
      <div className="absolute right-3 bottom-20 flex flex-col gap-5 items-center z-20">
        <ActionButton
          id={`like-btn-${reel.id}`}
          icon={reel.is_liked ? '❤️' : '🤍'}
          label={reel.like_count > 0 ? String(reel.like_count) : 'Like'}
          onClick={handleLike}
        />
        <ActionButton
          id={`save-btn-${reel.id}`}
          icon={reel.is_saved ? '🔖' : '🏷️'}
          label="Save"
          onClick={handleSave}
        />
        <ActionButton
          id={`comment-btn-${reel.id}`}
          icon="💬"
          label="Chat"
          onClick={() => setChatOpen(true)}
        />
        <ActionButton
          id={`share-btn-${reel.id}`}
          icon="↗️"
          label="Share"
          onClick={handleShare}
        />
      </div>

      {/* Chat / Comments drawer */}
      <ChatDrawer
        reel={reel}
        open={chatOpen}
        onClose={() => setChatOpen(false)}
      />
    </>
  )
}
