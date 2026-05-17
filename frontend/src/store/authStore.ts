import { create } from 'zustand'

interface AuthState {
  token: string | null
  setToken: (token: string, refresh: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  setToken: (token, refresh) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refresh)
    set({ token })
  },
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ token: null })
  },
}))
