import { Bell, CheckCheck, Calendar, MessageSquare, AlertCircle } from 'lucide-react'
import { useNotifications, useMarkRead, useMarkAllRead } from '@/hooks/use-notifications'
import { Card, Button, Badge, PageLoader, EmptyState } from '@/components/ui'
import type { Notification } from '@/types/api'

const typeIcons: Record<string, React.ReactNode> = {
  slot_booked: <Calendar className="h-4 w-4 text-blue-500" />,
  slot_started: <Calendar className="h-4 w-4 text-amber-500" />,
  slot_completed: <Calendar className="h-4 w-4 text-emerald-500" />,
  review_received: <MessageSquare className="h-4 w-4 text-primary-500" />,
  slot_cancelled: <AlertCircle className="h-4 w-4 text-red-500" />,
}

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'hozirgina'
  if (mins < 60) return `${mins} daqiqa oldin`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs} soat oldin`
  const days = Math.floor(hrs / 24)
  return `${days} kun oldin`
}

export function NotificationsPage() {
  const { data: notifications, isLoading } = useNotifications(50)
  const markRead = useMarkRead()
  const markAllRead = useMarkAllRead()

  const unreadCount = notifications?.filter((n) => !n.is_read).length ?? 0

  const handleMarkRead = (notif: Notification) => {
    if (!notif.is_read) {
      markRead.mutate(notif.id)
    }
  }

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="h-5 w-5 text-gray-400" />
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Bildirishnomalar
          </h1>
          {unreadCount > 0 && (
            <Badge variant="error">{unreadCount} yangi</Badge>
          )}
        </div>
        {unreadCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => markAllRead.mutate()}
            loading={markAllRead.isPending}
            icon={<CheckCheck className="h-4 w-4" />}
          >
            Hammasini o'qilgan
          </Button>
        )}
      </div>

      {isLoading ? (
        <PageLoader />
      ) : !notifications?.length ? (
        <EmptyState
          icon={<Bell className="h-10 w-10" />}
          title="Bildirishnomalar yo'q"
          description="Yangi bildirishnomalar bu yerda ko'rinadi"
        />
      ) : (
        <Card padding="none">
          <div className="divide-y divide-border">
            {notifications.map((notif) => (
              <button
                key={notif.id}
                onClick={() => handleMarkRead(notif)}
                className={`w-full flex items-start gap-3 px-4 py-3.5 text-left transition-colors hover:bg-surface-hover ${
                  !notif.is_read ? 'bg-primary-50/50 dark:bg-primary-900/10' : ''
                }`}
              >
                <div className="mt-0.5 shrink-0">
                  {typeIcons[notif.type] || <Bell className="h-4 w-4 text-gray-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${!notif.is_read ? 'font-semibold text-gray-900 dark:text-gray-100' : 'text-gray-700 dark:text-gray-300'}`}>
                    {notif.title || notif.type}
                  </p>
                  {notif.body && (
                    <p className="text-xs text-gray-500 mt-0.5 truncate">
                      {notif.body}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {timeAgo(notif.created_at)}
                  </p>
                </div>
                {!notif.is_read && (
                  <span className="mt-1.5 h-2 w-2 rounded-full bg-primary-500 shrink-0" />
                )}
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
