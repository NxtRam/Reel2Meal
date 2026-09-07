import LoginForm from '../components/auth/LoginForm'

export default function RestaurantLoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🏢</div>
          <h1 className="text-3xl font-extrabold gradient-text">Reel2Meal</h1>
          <p className="text-white/50 mt-1 text-sm">Restaurant Partner Portal</p>
        </div>

        <div className="glass rounded-2xl p-6 border border-orange-500/20 shadow-[0_0_40px_rgba(251,146,60,0.08)]">
          {/* Restaurant badge */}
          <div className="flex items-center gap-2 mb-5">
            <span className="text-2xl">👨‍🍳</span>
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">Restaurant Sign In</h2>
              <p className="text-white/40 text-xs">Post reels, manage your menu & orders</p>
            </div>
          </div>

          {/* Feature highlights */}
          <div className="flex gap-2 mb-5 flex-wrap">
            {['🎬 Post Reels', '📋 Manage Menu', '📦 Track Orders'].map((f) => (
              <span
                key={f}
                className="text-xs px-2.5 py-1 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 font-medium"
              >
                {f}
              </span>
            ))}
          </div>

          <LoginForm isRestaurant={true} />
        </div>
      </div>
    </div>
  )
}
