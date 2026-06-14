import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import {
  LayoutDashboard,
  CalendarClock,
  Search,
  Trophy,
  User,
  Bell,
  Settings,
  LogOut,
} from 'lucide-react'
import { useAuthStore } from '@/stores/auth'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/slots', icon: CalendarClock, label: 'Slotlar' },
  { to: '/search', icon: Search, label: 'Qidirish' },
  { to: '/leaderboard', icon: Trophy, label: 'Reyting' },
  { to: '/profile', icon: User, label: 'Profil' },
  { to: '/notifications', icon: Bell, label: 'Bildirishnomalar' },
  { to: '/settings', icon: Settings, label: 'Sozlamalar' },
]

export function Sidebar() {
  const logout = useAuthStore((s) => s.logout)

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-border bg-surface">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2.5 px-6 border-b border-border">
        <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
          <span className="text-white font-bold text-sm">P2P</span>
        </div>
        <span className="font-semibold text-gray-900 dark:text-gray-100">
          Peer Learn
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="flex flex-col gap-1" role="list">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                      : 'text-gray-600 hover:bg-surface-secondary hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100',
                  )
                }
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-border">
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-600 hover:bg-red-50 hover:text-red-600 dark:text-gray-400 dark:hover:bg-red-900/20 dark:hover:text-red-400 transition-colors"
        >
          <LogOut className="h-5 w-5" />
          Chiqish
        </button>
      </div>
    </aside>
  )
}
