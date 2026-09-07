import { BrowserRouter, Routes, Route } from 'react-router-dom'
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

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<FeedPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/login/restaurant" element={<RestaurantLoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/register/restaurant" element={<RestaurantRegisterPage />} />
        <Route path="/u/:username" element={<ProfilePage />} />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <OrdersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/post-reel"
          element={
            <ProtectedRoute>
              <PostReelPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
