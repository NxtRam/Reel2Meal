import { useAuthStore } from '../store/authStore'

export function useAuth() {
  const { user, token, login, register, registerRestaurant, logout, fetchMe } = useAuthStore()
  return {
    user,
    token,
    isAuthenticated: !!token,
    login,
    register,
    registerRestaurant,
    logout,
    fetchMe,
  }
}
