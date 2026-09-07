import FeedScroller from '../components/feed/FeedScroller'

export default function FeedPage() {
  return (
    <main
      className="bg-black overflow-hidden"
      style={{ height: '100dvh', paddingTop: '3.5rem' }}  /* dvh = dynamic viewport on mobile */
    >
      <div style={{ height: 'calc(100dvh - 3.5rem)', overflow: 'hidden' }}>
        <FeedScroller />
      </div>
    </main>
  )
}
