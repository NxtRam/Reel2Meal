import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function LoginForm({ isRestaurant = false }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, logout } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const userData = await login(email, password)
      // If logging in via restaurant portal, validate role
      if (isRestaurant && userData?.role !== 'restaurant') {
        logout()
        setError('This account is not a restaurant. Please use the customer sign-in page.')
        return
      }
      // If logging in via customer portal, block restaurants
      if (!isRestaurant && userData?.role === 'restaurant') {
        logout()
        setError('Restaurant accounts must sign in via the Restaurant Portal.')
        return
      }
      navigate('/')
    } catch (err) {
      const detail = err.response?.data?.detail;
      let errMsg = 'Login failed. Please try again.';
      if (typeof detail === 'string') errMsg = detail;
      else if (Array.isArray(detail) && detail.length > 0) errMsg = detail[0].msg;
      setError(errMsg);
    } finally {
      setLoading(false)
    }
  }

  return (
    <form id={isRestaurant ? 'restaurant-login-form' : 'login-form'} onSubmit={handleSubmit} className="flex flex-col gap-4">
      {error && (
        <p className="text-red-400 text-sm text-center bg-red-500/10 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-1.5">
        <label htmlFor="login-email" className="text-sm font-medium text-white/70">Email</label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
          className="bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="login-password" className="text-sm font-medium text-white/70">Password</label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          required
          className="bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors"
        />
      </div>

      <button
        id="login-submit-btn"
        type="submit"
        disabled={loading}
        className="gradient-bg text-white font-semibold py-3 rounded-xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 mt-1"
      >
        {loading ? 'Signing in…' : 'Sign In'}
      </button>

      <p className="text-center text-sm text-white/40">
        Don't have an account?{' '}
        <Link
          to={isRestaurant ? '/register/restaurant' : '/register'}
          className="text-brand-400 hover:underline font-medium"
        >
          {isRestaurant ? 'Register Restaurant' : 'Join Reel2Meal'}
        </Link>
      </p>

      {/* Cross-portal link */}
      <div className="border-t border-white/10 pt-3">
        <p className="text-center text-xs text-white/30">
          {isRestaurant ? (
            <>
              Customer?{' '}
              <Link to="/login" className="text-white/50 hover:text-white transition-colors">
                Customer Sign In →
              </Link>
            </>
          ) : (
            <>
              Own a restaurant?{' '}
              <Link to="/login/restaurant" className="text-white/50 hover:text-white transition-colors">
                Restaurant Portal →
              </Link>
            </>
          )}
        </p>
      </div>
    </form>
  )
}
