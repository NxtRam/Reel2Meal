import LoginForm from '../components/auth/LoginForm'

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🎬</div>
          <h1 className="text-3xl font-extrabold gradient-text">Reel2Meal</h1>
          <p className="text-white/50 mt-1 text-sm">Discover food through short videos</p>
        </div>

        <div className="glass rounded-2xl p-6 border border-white/10">
          {/* Customer badge */}
          <div className="flex items-center gap-2 mb-5">
            <span className="text-2xl">🍕</span>
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">Customer Sign In</h2>
              <p className="text-white/40 text-xs">Browse & order delicious food reels</p>
            </div>
          </div>
          <LoginForm isRestaurant={false} />
        </div>
      </div>
    </div>
  )
}
