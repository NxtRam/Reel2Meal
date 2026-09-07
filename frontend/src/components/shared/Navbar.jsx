import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10 h-14 flex items-center px-4 gap-4">
      <Link to="/" className="flex items-center gap-2 mr-auto">
        <span className="text-2xl">🎬</span>
        <span className="font-bold text-lg gradient-text">Reel2Meal</span>
      </Link>

      {isAuthenticated ? (
        <div className="flex items-center gap-3">
          {user?.role === 'restaurant' && (
            <Link
              to="/post-reel"
              id="navbar-post-reel-link"
              className="text-sm px-3 py-1.5 rounded-lg bg-brand-500/20 text-brand-400 hover:bg-brand-500/30 border border-brand-500/30 transition-all font-semibold flex items-center gap-1.5"
            >
              🎬 <span>Post Reel</span>
            </Link>
          )}
          <Link
            to="/orders"
            id="navbar-orders-link"
            className="text-sm px-3 py-1.5 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors hidden sm:block"
          >
            🛒 Orders
          </Link>
          <Link
            to={`/u/${user?.username}`}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.username}
                className="w-8 h-8 rounded-full object-cover ring-2 ring-brand-500"
              />
            ) : (
              <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center text-white font-bold text-sm">
                {user?.username?.[0]?.toUpperCase() ?? '?'}
              </div>
            )}
            <span className="text-sm font-medium hidden sm:block">{user?.username}</span>
          </Link>
          <button
            id="navbar-logout-btn"
            onClick={handleLogout}
            className="text-sm text-white/60 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/10"
          >
            Sign out
          </button>
        </div>
      ) : (
        <div className="flex gap-2 items-center">
          {/* Customer portal */}
          <Link
            to="/login"
            id="navbar-login-link"
            className="text-sm px-3 py-1.5 rounded-lg border border-white/20 hover:bg-white/10 transition-colors text-white/80"
          >
            🍕 Sign In
          </Link>
          <Link
            to="/register"
            id="navbar-register-link"
            className="text-sm px-3 py-1.5 rounded-lg gradient-bg font-medium hover:opacity-90 transition-opacity hidden sm:block"
          >
            Join
          </Link>

          {/* Divider */}
          <span className="text-white/20 hidden sm:block">|</span>

          {/* Restaurant portal */}
          <Link
            to="/login/restaurant"
            id="navbar-restaurant-login-link"
            className="text-sm px-3 py-1.5 rounded-lg border border-brand-500/30 text-brand-400 hover:bg-brand-500/10 transition-colors hidden sm:flex items-center gap-1"
          >
            🏢 Restaurant
          </Link>
        </div>
      )}
    </nav>
  )
}
