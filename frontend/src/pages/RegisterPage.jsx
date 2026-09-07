import RegisterForm from '../components/auth/RegisterForm'

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🎬</div>
          <h1 className="text-3xl font-extrabold gradient-text">Reel2Meal</h1>
          <p className="text-white/50 mt-1 text-sm">Join the food reel community</p>
        </div>

        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-center gap-2 mb-5">
            <span className="text-2xl">🍕</span>
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">Create Customer Account</h2>
              <p className="text-white/40 text-xs">Discover, watch & order amazing food</p>
            </div>
          </div>
          <RegisterForm isRestaurant={false} />
        </div>
      </div>
    </div>
  )
}
