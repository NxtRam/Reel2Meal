import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Navbar from './components/shared/Navbar'
import ProtectedRoute from './components/shared/ProtectedRoute'
import FeedPage from './pages/FeedPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import OrdersPage from './pages/OrdersPage'
import PostReelPage from './pages/PostReelPage'
import RestaurantLoginPage from './pages/RestaurantLoginPage'
import RestaurantRegisterPage from './pages/RestaurantRegisterPage'

/** Redirects already-logged-in users to the feed */
function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        {/* Protected: redirect to /login if not signed in */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <FeedPage />
            </ProtectedRoute>
          }
        />

        {/* Public: redirect to / if already signed in */}
        <Route path="/login"               element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/login/restaurant"    element={<PublicRoute><RestaurantLoginPage /></PublicRoute>} />
        <Route path="/register"            element={<PublicRoute><RegisterPage /></PublicRoute>} />
        <Route path="/register/restaurant" element={<PublicRoute><RestaurantRegisterPage /></PublicRoute>} />

        {/* Profile — accessible without login */}
        <Route path="/u/:username" element={<ProfilePage />} />

        {/* Protected */}
        <Route path="/orders"    element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
        <Route path="/post-reel" element={<ProtectedRoute><PostReelPage /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
