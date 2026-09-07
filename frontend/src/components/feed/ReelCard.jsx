import { useRef, useEffect, useState, useCallback } from 'react'
import ReelMeta from './ReelMeta'
import ReelActions from './ReelActions'
import MenuDrawer from '../menu/MenuDrawer'
import { isYouTubeUrl, getYouTubeEmbedUrl } from '../../utils/youtube'

/**
 * ReelCard — Instagram / TikTok–style full-screen food reel.
 *
 * Video features:
 *   ✅ Autoplay (muted) when isActive
 *   ✅ Tap to play / pause with animated icon
 *   ✅ Double-tap anywhere → heart burst (like)
 *   ✅ Progress bar scrubbing at top
 *   ✅ Sound toggle 🔇 / 🔊
 *   ✅ Smooth thumbnail → video transition
 *
 * Music features:
 *   ✅ Background audio track per reel
 *   ✅ Spinning vinyl disc UI (TikTok style)
 *   ✅ Music toggle 🎵 / 🔕
 *   ✅ Audio syncs with video active state
 *   ✅ Fade-in song title when music starts
 */
export default function ReelCard({
  reel,
  isActive,
  globalMuted,
  setGlobalMuted,
  globalMusicOn,
  setGlobalMusicOn,
}) {
  const videoRef = useRef(null)
  const iframeRef = useRef(null)
  const audioRef = useRef(null)
  const tapTimeout = useRef(null)

  const [paused,     setPaused]     = useState(false)
  const [menuOpen,   setMenuOpen]   = useState(false)
  const [progress,   setProgress]   = useState(0)
  const [showPause,  setShowPause]  = useState(false)
  const [heartPos,   setHeartPos]   = useState(null)
  const [videoReady, setVideoReady] = useState(false)
  const [showSong,   setShowSong]   = useState(false)

  const muted = globalMuted
  const musicOn = globalMusicOn

  // Detect YouTube URL and build embed URL (rebuild key when muted changes to reload iframe)
  const ytEmbed = getYouTubeEmbedUrl(reel.video_url, muted)
  const isYT = !!ytEmbed
  // iframeKey forces the iframe to fully reload when mute state changes
  const iframeKey = isYT ? `${reel.id}-${muted ? 'muted' : 'unmuted'}` : null

  // ── Autoplay / autopause when reel enters/leaves viewport ─────────────────
  useEffect(() => {
    // YouTube iframes are auto-controlled via URL params; only manage native video
    if (isYT) return
    const video = videoRef.current
    const audio = audioRef.current
    if (!video) return

    if (isActive) {
      video.currentTime = 0
      video.muted = muted
      video.play().catch(() => setPaused(true))
      setPaused(false)

      // Play music if toggled on
      if (audio) {
        audio.currentTime = 0
        if (musicOn) {
          audio.play().catch(() => {})
        } else {
          audio.pause()
        }
      }
    } else {
      video.pause()
      setProgress(0)
      audio?.pause()
    }
  }, [isActive, isYT])

  // ── Sync video mute property ──────────────────────────────────────────────
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = muted
    }
  }, [muted])

  // ── Sync music with musicOn toggle ────────────────────────────────────────
  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !isActive) return
    if (musicOn) {
      audio.play().catch(() => {})
      setShowSong(true)
      const timer = setTimeout(() => setShowSong(false), 3000)
      return () => clearTimeout(timer)
    } else {
      audio.pause()
    }
  }, [musicOn, isActive])

  // ── Progress bar ──────────────────────────────────────────────────────────
  const handleTimeUpdate = useCallback(() => {
    const v = videoRef.current
    if (v && v.duration) setProgress((v.currentTime / v.duration) * 100)
  }, [])

  // ── Tap handler: single = play/pause, double = like heart ─────────────────
  const handleTap = useCallback((e) => {
    if (tapTimeout.current) {
      clearTimeout(tapTimeout.current)
      tapTimeout.current = null
      // Double-tap — heart burst
      setHeartPos({ x: e.clientX, y: e.clientY })
      setTimeout(() => setHeartPos(null), 900)
      return
    }
    tapTimeout.current = setTimeout(() => {
      tapTimeout.current = null

      if (isYT) {
        // Control YouTube iframe via postMessage
        const iframe = iframeRef.current
        if (!iframe) return
        if (paused) {
          iframe.contentWindow.postMessage(
            JSON.stringify({ event: 'command', func: 'playVideo', args: [] }), '*'
          )
          setPaused(false)
          setShowPause(false)
        } else {
          iframe.contentWindow.postMessage(
            JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), '*'
          )
          setPaused(true)
          setShowPause(true)
          setTimeout(() => setShowPause(false), 1500)
        }
      } else {
        // Control native <video> element
        const v = videoRef.current
        if (!v) return
        if (v.paused) {
          v.play().catch(() => {})
          setPaused(false)
          setShowPause(false)
        } else {
          v.pause()
          setPaused(true)
          setShowPause(true)
          setTimeout(() => setShowPause(false), 1500)
        }
      }
    }, 220)
  }, [isYT, paused])

  // ── Toggle video sound ────────────────────────────────────────────
  const toggleMute = useCallback((e) => {
    e.stopPropagation()
    setGlobalMuted((m) => {
      const nextMuted = !m
      // For non-YT videos, music and video sound are linked
      if (!isYT) setGlobalMusicOn(!nextMuted)
      return nextMuted
    })
  }, [setGlobalMuted, setGlobalMusicOn, isYT])

  // ── Toggle music track ────────────────────────────────────────────────────
  const toggleMusic = useCallback((e) => {
    e.stopPropagation()
    setGlobalMusicOn((on) => {
      const nextOn = !on
      setGlobalMuted(!nextOn)
      return nextOn
    })
  }, [setGlobalMuted, setGlobalMusicOn])

  const hasMusicTrack = !!reel.audio_url

  return (
    <div
      id={`reel-card-${reel.id}`}
      className="relative w-full h-full flex-shrink-0 bg-black overflow-hidden select-none"
    >
      {/* ── Thumbnail (shows before video loads) ──────────────────── */}
      {!videoReady && reel.thumbnail_url && (
        <img
          src={reel.thumbnail_url}
          alt={reel.title}
          className="absolute inset-0 w-full h-full object-cover"
        />
      )}

      {/* ── VIDEO or YOUTUBE IFRAME ─────────────────────────────── */}
      {isYT ? (
        // YouTube embed via iframe — key changes when muted toggles, forcing reload
        <iframe
          ref={iframeRef}
          key={iframeKey}
          src={isActive ? ytEmbed : ''}
          title={reel.title}
          allow="autoplay; encrypted-media; picture-in-picture"
          allowFullScreen
          className="absolute inset-0 w-full h-full border-0 pointer-events-none"
          style={{ objectFit: 'cover' }}
        />
      ) : (
        <video
          ref={videoRef}
          src={reel.video_url}
          poster={reel.thumbnail_url}
          loop
          muted={muted}
          playsInline
          preload="metadata"
          onTimeUpdate={handleTimeUpdate}
          onCanPlay={() => setVideoReady(true)}
          onLoadedData={() => setVideoReady(true)}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ${videoReady ? 'opacity-100' : 'opacity-0'}`}
          aria-label={reel.title}
        />
      )}

      {/* ── Transparent tap overlay — covers full screen, below UI controls ── */}
      <div
        className="absolute inset-0 z-10 cursor-pointer"
        onClick={(e) => { e.stopPropagation(); handleTap(e) }}
        aria-label="Tap to pause / play"
      />

      {/* ── BACKGROUND AUDIO TRACK ────────────────────────────────── */}
      {hasMusicTrack && (
        <audio
          ref={audioRef}
          src={reel.audio_url}
          loop
          preload="none"
          style={{ display: 'none' }}
        />
      )}

      {/* ── Gradient overlays ─────────────────────────────────────── */}
      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />
      <div className="absolute inset-x-0 bottom-0 h-72 bg-gradient-to-t from-black/95 via-black/50 to-transparent pointer-events-none" />

      {/* ── Progress bar (top edge) ───────────────────────────────── */}
      <div className="absolute top-0 inset-x-0 h-0.5 bg-white/15 z-10">
        <div
          className="h-full bg-white/90 transition-all duration-200 ease-linear"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* ── Top-right controls row ────────────────────────────────── */}
      <div className="absolute top-4 right-4 z-20 flex flex-col gap-2 items-center">
        {/* Sound toggle */}
        <button
          id={`mute-btn-${reel.id}`}
          onClick={toggleMute}
          className="w-9 h-9 rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center text-base hover:bg-black/70 transition-all"
          aria-label={muted ? 'Unmute' : 'Mute'}
        >
          {muted ? '🔇' : '🔊'}
        </button>

        {/* Music toggle — hidden for YouTube (YT has its own audio) */}
        {hasMusicTrack && !isYT && (
          <button
            id={`music-btn-${reel.id}`}
            onClick={toggleMusic}
            className={`w-9 h-9 rounded-full backdrop-blur-md flex items-center justify-center text-base transition-all ${
              musicOn
                ? 'bg-brand-500/80 hover:bg-brand-600/80'
                : 'bg-black/50 hover:bg-black/70'
            }`}
            aria-label={musicOn ? 'Stop music' : 'Play music'}
          >
            {musicOn ? '🎵' : '🔕'}
          </button>
        )}
      </div>

      {/* ── YouTube "tap to hear" hint (shown when muted & active) ── */}
      {isYT && isActive && muted && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-20 animate-fade-in">
          <button
            onClick={toggleMute}
            className="flex items-center gap-2 bg-black/70 backdrop-blur-md rounded-full px-4 py-2 border border-white/15 hover:bg-black/90 transition-all active:scale-95"
          >
            <span className="text-sm">🔇</span>
            <span className="text-white text-xs font-semibold">Tap to hear audio</span>
          </button>
        </div>
      )}

      {/* ── Spinning vinyl disc (TikTok style) ───────────────────── */}
      {hasMusicTrack && isActive && (
        <div className="absolute bottom-36 right-3 z-20">
          <div
            className={`w-14 h-14 rounded-full border-4 border-white/20 overflow-hidden ${
              musicOn ? 'animate-spin-slow' : ''
            }`}
            style={{ animationDuration: '3s' }}
          >
            <img
              src={reel.thumbnail_url}
              alt="Now playing"
              className="w-full h-full object-cover"
            />
            {/* Centre hole */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-black/80 border border-white/30" />
            </div>
          </div>
          {/* Floating music notes */}
          {musicOn && (
            <div className="absolute -top-1 -left-2 text-xs animate-bounce">♪</div>
          )}
        </div>
      )}

      {/* ── Now-playing toast ─────────────────────────────────────── */}
      {showSong && hasMusicTrack && (
        <div className="absolute top-16 inset-x-4 z-20 flex items-center gap-2 bg-black/70 backdrop-blur-md rounded-full px-4 py-2 animate-fade-in">
          <span className="text-sm animate-spin-slow inline-block" style={{ animationDuration: '2s' }}>💿</span>
          <p className="text-white text-xs font-medium truncate flex-1">
            ♪ Now Playing · Reel2Meal Mix
          </p>
        </div>
      )}

      {/* ── Play / Pause flash icon (centre) ─────────────────────── */}
      {showPause && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="w-20 h-20 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center animate-fade-in">
            <span className="text-4xl ml-1">▶</span>
          </div>
        </div>
      )}
      {paused && !showPause && isActive && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <div className="w-20 h-20 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center">
            <span className="text-4xl ml-1">▶</span>
          </div>
        </div>
      )}

      {/* ── Double-tap heart burst ────────────────────────────────── */}
      {heartPos && (
        <div
          className="absolute pointer-events-none z-30 text-5xl animate-pop"
          style={{
            left: heartPos.x - 30,
            top: heartPos.y - 30,
            filter: 'drop-shadow(0 0 12px rgba(255,50,100,0.9))',
          }}
        >
          ❤️
        </div>
      )}

      {/* ── Food description badge ────────────────────────────────── */}
      {reel.description && (
        <div className="absolute top-16 left-4 right-16 z-10 max-w-[240px]">
          <p className="text-white/70 text-xs leading-snug line-clamp-2 drop-shadow-lg">
            {reel.description}
          </p>
        </div>
      )}

      {/* ── Meta overlay (bottom-left) ───────────────────────────── */}
      <ReelMeta reel={reel} onMenuOpen={() => setMenuOpen(true)} />

      {/* ── Action rail (right) ───────────────────────────────────── */}
      <ReelActions reel={reel} />

      {/* ── Food menu drawer ─────────────────────────────────────── */}
      {menuOpen && (
        <MenuDrawer reelId={reel.id} onClose={() => setMenuOpen(false)} />
      )}
    </div>
  )
}
