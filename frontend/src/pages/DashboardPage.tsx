import { Link } from 'react-router-dom'
import {
  CalendarClock,
  Coins,
  Star,
  TrendingUp,
  Zap,
  ArrowRight,
} from 'lucide-react'
import { useDashboard } from '@/hooks/use-dashboard'
import { Card, Badge, Avatar, PageLoader, EmptyState } from '@/components/ui'
import { SlotCard } from '@/components/slots/SlotCard'

export function DashboardPage() {
  const { data, isLoading } = useDashboard()

  if (isLoading) return <PageLoader />
  if (!data) return null

  const { user, xp_to_next_level, active_slots } = data

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div className="flex items-center gap-4">
        <Avatar src={user.avatar_url} name={user.first_name || user.school21_login} size="xl" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Salom, {user.first_name || user.school21_login}!
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {user.campus && `📍 ${user.campus}`}
            {user.current_location && ` • ${user.current_location}`}
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          icon={<TrendingUp className="h-5 w-5 text-primary-500" />}
          label="Level"
          value={user.level}
          sub={`${user.xp} XP (yana ${xp_to_next_level})`}
        />
        <StatCard
          icon={<Zap className="h-5 w-5 text-amber-500" />}
          label="Peer Points"
          value={user.peer_points}
        />
        <StatCard
          icon={<Coins className="h-5 w-5 text-emerald-500" />}
          label="Peer Coins"
          value={user.peer_coins}
        />
        <StatCard
          icon={<Star className="h-5 w-5 text-blue-500" />}
          label="Yo'nalish"
          value={user.main_track || '—'}
        />
      </div>

      {/* XP Progress */}
      <Card>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Level {user.level} → Level {user.level + 1}
          </span>
          <span className="text-xs text-gray-500">{xp_to_next_level} XP qoldi</span>
        </div>
        <div className="h-2.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
          <div
            className="h-full rounded-full bg-linear-to-r from-primary-500 to-primary-400 transition-all"
            style={{ width: `${Math.max(5, 100 - (xp_to_next_level / (user.xp + xp_to_next_level)) * 100)}%` }}
          />
        </div>
      </Card>

      {/* Active Slots */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Aktiv slotlar
          </h2>
          <Link
            to="/slots"
            className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Hammasi <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {active_slots.length === 0 ? (
          <EmptyState
            icon={<CalendarClock className="h-10 w-10" />}
            title="Aktiv slotlar yo'q"
            description="Yangi slot yarating yoki mavjud slotni qidiring"
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {active_slots.map((slot) => (
              <SlotCard key={slot.id} slot={slot} userId={user.id} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode
  label: string
  value: string | number
  sub?: string
}) {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        {icon}
        <span className="text-xs text-gray-500 dark:text-gray-400">{label}</span>
      </div>
      <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
      {sub && <p className="text-xs text-gray-500">{sub}</p>}
    </Card>
  )
}
