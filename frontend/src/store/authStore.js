import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../api/authApi'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      isAuthenticated: () => !!get().token,

      login: async (email, password) => {
        const data = await authApi.login({ email, password })
        set({ token: data.access_token })
        const me = await authApi.me()
        set({ user: me })
        return me
      },

      register: async (username, email, password) => {
        await authApi.register({ username, email, password })
        return get().login(email, password)
      },

      registerRestaurant: async (restaurantData) => {
        await authApi.registerRestaurant(restaurantData)
        return get().login(restaurantData.email, restaurantData.password)
      },

      logout: () => set({ user: null, token: null }),

      fetchMe: async () => {
        if (!get().token) return
        try {
          const me = await authApi.me()
          set({ user: me })
        } catch {
          set({ user: null, token: null })
        }
      },
    }),
    { name: 'r2m-auth', partialize: (s) => ({ token: s.token }) }
  )
)
