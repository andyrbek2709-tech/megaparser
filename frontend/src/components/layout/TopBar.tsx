import { useAuthStore } from '../../store/authStore'

export function TopBar() {
  const logout = useAuthStore((s) => s.logout)
  return (
    <header className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-end px-6">
      <button
        onClick={logout}
        className="text-sm text-gray-400 hover:text-white transition-colors"
      >
        Logout
      </button>
    </header>
  )
}
