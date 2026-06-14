import { CalendarClock, MapPin, Monitor, Users } from 'lucide-react'
import type { Slot } from '@/types/api'
import { Card, Badge } from '@/components/ui'

interface SlotCardProps {
  slot: Slot
  userId: string
  onClick?: () => void
}

const statusConfig: Record<string, { label: string; variant: 'success' | 'warning' | 'info' | 'error' | 'default' }> = {
  open: { label: 'Ochiq', variant: 'success' },
  booked: { label: 'Band', variant: 'info' },
  in_progress: { label: 'Jarayonda', variant: 'warning' },
  completed: { label: 'Tugallandi', variant: 'success' },
  cancelled: { label: 'Bekor', variant: 'error' },
  absent: { label: 'Kelmadi', variant: 'error' },
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleString('uz-UZ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function SlotCard({ slot, userId, onClick }: SlotCardProps) {
  const isReviewer = slot.reviewer_id === userId
  const config = statusConfig[slot.status] || { label: slot.status, variant: 'default' as const }

  return (
    <Card hover={!!onClick} onClick={onClick} className="space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-gray-900 dark:text-gray-100 text-sm">
            {slot.reviewer_project}
          </p>
          <Badge variant={isReviewer ? 'purple' : 'info'} className="mt-1">
            {isReviewer ? 'O\'qituvchi' : 'O\'quvchi'}
          </Badge>
        </div>
        <Badge variant={config.variant}>{config.label}</Badge>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
        <span className="flex items-center gap-1">
          <CalendarClock className="h-3.5 w-3.5" />
          {formatTime(slot.start_time)}
        </span>
        <span className="flex items-center gap-1">
          {slot.is_online ? (
            <>
              <Monitor className="h-3.5 w-3.5" />
              Online
            </>
          ) : (
            <>
              <MapPin className="h-3.5 w-3.5" />
              {slot.campus}
            </>
          )}
        </span>
        {slot.reviewee_id && (
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            Ikki kishi
          </span>
        )}
      </div>
    </Card>
  )
}
