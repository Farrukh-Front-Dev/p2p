import { useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import { X, LayoutDashboard, CalendarClock, Search, Trophy, User, Bell, Settings } from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/slots', icon: CalendarClock, label: 'Slotlar' },
  { to: '/search', icon: Search, label: 'Qidirish' },
  { to: '/leaderboard', icon: Trophy, label: 'Reyting' },
  { to: '/profile', icon: User, label: 'Profil' },
  { to: '/notifications', icon: Bell, label: 'Bildirishnomalar' },
  { to: '/settings', icon: Settings, label: 'Sozlamalar' },
]

interface MobileNavProps {
  open: boolean
  onClose: () => void
}

export function MobileNav({ open, onClose }: MobileNavProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 left-0 z-50 w-72 bg-surface shadow-xl lg:hidden animate-in slide-in-from-left duration-200">
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">P2P</span>
            </div>
            <span className="font-semibold text-gray-900 dark:text-gray-100">
              Peer Learn
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-500 hover:bg-surface-secondary"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="px-3 py-4">
          <ul className="flex flex-col gap-1" role="list">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  onClick={onClose}
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
      </div>
    </>
  )
}
