import RegisterForm from '../components/auth/RegisterForm'

export default function RestaurantRegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🏢</div>
          <h1 className="text-3xl font-extrabold gradient-text">Reel2Meal</h1>
          <p className="text-white/50 mt-1 text-sm">Restaurant Partner Portal</p>
        </div>

        <div className="glass rounded-2xl p-6 border border-orange-500/20 shadow-[0_0_40px_rgba(251,146,60,0.08)]">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">👨‍🍳</span>
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">Register Your Restaurant</h2>
              <p className="text-white/40 text-xs">Start posting reels & growing your orders</p>
            </div>
          </div>

          {/* What you get */}
          <div className="bg-white/5 rounded-xl p-3 mb-5 mt-3 border border-white/10">
            <p className="text-xs text-white/40 font-semibold mb-2 uppercase tracking-wider">What you get</p>
            <ul className="flex flex-col gap-1.5">
              {[
                '🎬 Post short food reels to attract customers',
                '📋 Add your menu with prices & categories',
                '📦 Receive & track orders in real-time',
              ].map((item) => (
                <li key={item} className="text-xs text-white/70 flex items-start gap-2">
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <RegisterForm isRestaurant={true} />
        </div>
      </div>
    </div>
  )
}
