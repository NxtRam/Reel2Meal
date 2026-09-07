import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function RegisterForm({ isRestaurant = false }) {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirm: '',
    restaurantName: '',
    restaurantAddress: '',
    restaurantCity: '',
    restaurantContact: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register, registerRestaurant } = useAuth()
  const navigate = useNavigate()

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      if (isRestaurant) {
        await registerRestaurant({
          username: form.username,
          email: form.email,
          password: form.password,
          restaurant_name: form.restaurantName,
          restaurant_address: form.restaurantAddress || null,
          restaurant_city: form.restaurantCity || null,
          restaurant_contact: form.restaurantContact || null,
        })
      } else {
        await register(form.username, form.email, form.password)
      }
      navigate('/')
    } catch (err) {
      const detail = err.response?.data?.detail;
      let errMsg = 'Registration failed. Please try again.';
      if (typeof detail === 'string') errMsg = detail;
      else if (Array.isArray(detail) && detail.length > 0) errMsg = detail[0].msg;
      setError(errMsg);
    } finally {
      setLoading(false)
    }
  }

  const baseFields = [
    { id: 'reg-username', key: 'username', label: 'Username', type: 'text', placeholder: isRestaurant ? 'pizzahub_official' : 'foodie_dev', required: true },
    { id: 'reg-email', key: 'email', label: 'Email', type: 'email', placeholder: 'you@example.com', required: true },
    { id: 'reg-password', key: 'password', label: 'Password', type: 'password', placeholder: '••••••••', required: true },
    { id: 'reg-confirm', key: 'confirm', label: 'Confirm Password', type: 'password', placeholder: '••••••••', required: true },
  ]

  const restaurantFields = [
    { id: 'reg-rest-name', key: 'restaurantName', label: 'Restaurant Name', type: 'text', placeholder: 'Gourmet Grill', required: true },
    { id: 'reg-rest-address', key: 'restaurantAddress', label: 'Address', type: 'text', placeholder: '123 Foodie Lane', required: false },
    { id: 'reg-rest-city', key: 'restaurantCity', label: 'City', type: 'text', placeholder: 'Mumbai', required: false },
    { id: 'reg-rest-contact', key: 'restaurantContact', label: 'Contact Number', type: 'text', placeholder: '9876543210', required: false },
  ]

  const activeFields = isRestaurant ? [...restaurantFields, ...baseFields] : baseFields

  return (
    <form
      id={isRestaurant ? 'restaurant-register-form' : 'register-form'}
      onSubmit={handleSubmit}
      className="flex flex-col gap-4"
    >
      {error && (
        <p className="text-red-400 text-sm text-center bg-red-500/10 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-4">
        {activeFields.map(({ id, key, label, type, placeholder, required }) => (
          <div key={key} className="flex flex-col gap-1.5">
            <label htmlFor={id} className="text-sm font-medium text-white/70">
              {label} {required && <span className="text-brand-500">*</span>}
            </label>
            <input
              id={id}
              type={type}
              value={form[key]}
              onChange={set(key)}
              placeholder={placeholder}
              required={required}
              minLength={key === 'password' || key === 'confirm' ? 8 : undefined}
              className="bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>
        ))}
      </div>

      <button
        id={isRestaurant ? 'restaurant-register-submit-btn' : 'register-submit-btn'}
        type="submit"
        disabled={loading}
        className="gradient-bg text-white font-semibold py-3 rounded-xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 mt-1"
      >
        {loading ? 'Creating account…' : isRestaurant ? 'Register Restaurant' : 'Create Account'}
      </button>

      <p className="text-center text-sm text-white/40">
        Already have an account?{' '}
        <Link
          to={isRestaurant ? '/login/restaurant' : '/login'}
          className="text-brand-400 hover:underline font-medium"
        >
          Sign in
        </Link>
      </p>

      {/* Cross-portal link */}
      <div className="border-t border-white/10 pt-3">
        <p className="text-center text-xs text-white/30">
          {isRestaurant ? (
            <>
              Registering as a customer?{' '}
              <Link to="/register" className="text-white/50 hover:text-white transition-colors">
                Customer Sign Up →
              </Link>
            </>
          ) : (
            <>
              Own a restaurant?{' '}
              <Link to="/register/restaurant" className="text-white/50 hover:text-white transition-colors">
                Register your Restaurant →
              </Link>
            </>
          )}
        </p>
      </div>
    </form>
  )
}
