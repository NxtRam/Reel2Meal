/**
 * Detects YouTube URLs (both full and Shorts) and returns the embed URL.
 * Returns null if the URL is not a YouTube URL.
 *
 * Supported input formats:
 *   https://www.youtube.com/watch?v=VIDEO_ID
 *   https://youtu.be/VIDEO_ID
 *   https://youtube.com/shorts/VIDEO_ID
 *   https://www.youtube.com/shorts/VIDEO_ID?si=...
 *
 * @param {string} url - The original video URL
 * @param {boolean} muted - Whether the video should be muted (default: true for autoplay)
 */
export function getYouTubeEmbedUrl(url, muted = true) {
  if (!url) return null

  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace('www.', '')

    if (host !== 'youtube.com' && host !== 'youtu.be') return null

    let videoId = null

    // youtu.be/VIDEO_ID
    if (host === 'youtu.be') {
      videoId = parsed.pathname.slice(1).split('?')[0]
    }
    // youtube.com/shorts/VIDEO_ID
    else if (parsed.pathname.startsWith('/shorts/')) {
      videoId = parsed.pathname.replace('/shorts/', '').split('?')[0]
    }
    // youtube.com/watch?v=VIDEO_ID
    else if (parsed.searchParams.has('v')) {
      videoId = parsed.searchParams.get('v')
    }

    if (!videoId) return null

    const muteParam = muted ? 1 : 0

    // Build the embed URL. mute=0 enables audio (requires user interaction first per browser policy).
    return `https://www.youtube.com/embed/${videoId}?autoplay=1&loop=1&playlist=${videoId}&controls=0&modestbranding=1&playsinline=1&mute=${muteParam}&rel=0&enablejsapi=1`
  } catch {
    return null
  }
}

/**
 * Returns true if the URL is a YouTube video link.
 */
export function isYouTubeUrl(url) {
  return getYouTubeEmbedUrl(url) !== null
}
