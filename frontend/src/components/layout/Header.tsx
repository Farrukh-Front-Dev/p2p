import { Bell, Menu } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useDashboard } from '@/hooks/use-dashboard'
import { Avatar } from '@/components/ui'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { data } = useDashboard()
  const user = data?.user
  const unread = data?.unread_notifications ?? 0

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-border bg-surface/80 backdrop-blur-sm px-4 sm:px-6">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-surface-secondary"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <Link
          to="/notifications"
          className="relative p-2 rounded-lg text-gray-500 hover:bg-surface-secondary transition-colors"
          aria-label={`Bildirishnomalar${unread > 0 ? ` (${unread} yangi)` : ''}`}
        >
          <Bell className="h-5 w-5" />
          {unread > 0 && (
            <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-error text-[10px] font-bold text-white">
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </Link>

        {/* User avatar */}
        <Link to="/profile" className="flex items-center gap-2">
          <Avatar
            src={user?.avatar_url}
            name={user?.first_name || user?.school21_login}
            size="sm"
          />
          <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300">
            {user?.school21_login}
          </span>
        </Link>
      </div>
    </header>
  )
}
