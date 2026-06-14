import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  CalendarClock,
  MapPin,
  Monitor,
  Play,
  CheckCircle,
  XCircle,
  UserX,
  Clock,
} from 'lucide-react'
import { useSlot, useStartSlot, useFinishSlot, useCancelSlot } from '@/hooks/use-slots'
import { useDashboard } from '@/hooks/use-dashboard'
import { Button, Card, Badge, PageLoader } from '@/components/ui'
import { toast } from '@/components/ui/Toast'
import type { Slot } from '@/types/api'

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('uz-UZ', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const statusMap: Record<string, { label: string; variant: 'success' | 'warning' | 'info' | 'error' | 'default' }> = {
  open: { label: 'Ochiq', variant: 'success' },
  booked: { label: 'Band qilingan', variant: 'info' },
  in_progress: { label: 'Jarayonda', variant: 'warning' },
  completed: { label: 'Tugallandi', variant: 'success' },
  cancelled: { label: 'Bekor qilingan', variant: 'error' },
  absent: { label: 'Kelmadi', variant: 'error' },
}

export function SlotDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: dashboard } = useDashboard()
  const { data: slot, isLoading } = useSlot(id || '')
  const startSlot = useStartSlot()
  const finishSlot = useFinishSlot()
  const cancelSlot = useCancelSlot()

  const userId = dashboard?.user.id

  if (isLoading) return <PageLoader />
  if (!slot || !userId) return null

  const isReviewer = slot.reviewer_id === userId
  const status = statusMap[slot.status] || { label: slot.status, variant: 'default' as const }

  const handleStart = async () => {
    try {
      await startSlot.mutateAsync(slot.id)
      toast.success("Slot boshlandi!")
    } catch {
      toast.error("Slotni boshlashda xatolik")
    }
  }

  const handleFinish = async () => {
    try {
      await finishSlot.mutateAsync(slot.id)
      toast.success("Slot tugallandi!")
    } catch {
      toast.error("Slotni tugatishda xatolik")
    }
  }

  const handleCancel = async () => {
    try {
      await cancelSlot.mutateAsync({ id: slot.id, reason: 'Bekor qilindi' })
      toast.info("Slot bekor qilindi")
      navigate('/slots')
    } catch {
      toast.error("Bekor qilishda xatolik")
    }
  }

  return (
    <div className="space-y-5 max-w-2xl">
      {/* Back button */}
      <button
        onClick={() => navigate('/slots')}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Slotlarga qaytish
      </button>

      {/* Header */}
      <Card padding="lg">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {slot.reviewer_project}
            </h1>
            <Badge variant={isReviewer ? 'purple' : 'info'} className="mt-2">
              {isReviewer ? "O'qituvchi sifatida" : "O'quvchi sifatida"}
            </Badge>
          </div>
          <Badge variant={status.variant}>{status.label}</Badge>
        </div>

        {/* Details */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <InfoRow
            icon={<CalendarClock className="h-4 w-4 text-gray-400" />}
            label="Boshlanish"
            value={formatDateTime(slot.start_time)}
          />
          <InfoRow
            icon={<Clock className="h-4 w-4 text-gray-400" />}
            label="Tugash"
            value={formatDateTime(slot.end_time)}
          />
          <InfoRow
            icon={slot.is_online ? <Monitor className="h-4 w-4 text-gray-400" /> : <MapPin className="h-4 w-4 text-gray-400" />}
            label="Joylashuv"
            value={slot.is_online ? 'Online' : slot.campus}
          />
          {slot.duration_minutes && (
            <InfoRow
              icon={<Clock className="h-4 w-4 text-gray-400" />}
              label="Davomiyligi"
              value={`${slot.duration_minutes} daqiqa`}
            />
          )}
        </div>

        {slot.reviewee_project && (
          <div className="mt-4 p-3 bg-surface-secondary rounded-lg">
            <p className="text-xs text-gray-500 mb-1">O'quvchi loyihasi</p>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {slot.reviewee_project}
            </p>
          </div>
        )}
      </Card>

      {/* Actions */}
      <SlotActions
        slot={slot}
        isReviewer={isReviewer}
        onStart={handleStart}
        onFinish={handleFinish}
        onCancel={handleCancel}
        loading={startSlot.isPending || finishSlot.isPending || cancelSlot.isPending}
      />

      {/* Timeline */}
      <Card>
        <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Vaqt chizig'i</h3>
        <div className="space-y-3">
          <TimelineItem
            label="Yaratilgan"
            time={formatDateTime(slot.start_time)}
            done
          />
          {slot.reviewee_id && (
            <TimelineItem label="Band qilingan" done />
          )}
          {slot.actual_start && (
            <TimelineItem
              label="Boshlangan"
              time={formatDateTime(slot.actual_start)}
              done
            />
          )}
          {slot.actual_end && (
            <TimelineItem
              label="Tugallangan"
              time={formatDateTime(slot.actual_end)}
              done
            />
          )}
        </div>
      </Card>
    </div>
  )
}

function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-2">
      <span className="mt-0.5 shrink-0">{icon}</span>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="font-medium text-gray-900 dark:text-gray-100">{value}</p>
      </div>
    </div>
  )
}

function SlotActions({
  slot,
  isReviewer,
  onStart,
  onFinish,
  onCancel,
  loading,
}: {
  slot: Slot
  isReviewer: boolean
  onStart: () => void
  onFinish: () => void
  onCancel: () => void
  loading: boolean
}) {
  if (slot.status === 'completed' || slot.status === 'cancelled' || slot.status === 'absent') {
    return null
  }

  return (
    <Card>
      <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">Amallar</h3>
      <div className="flex flex-wrap gap-2">
        {slot.status === 'booked' && isReviewer && (
          <Button
            onClick={onStart}
            loading={loading}
            icon={<Play className="h-4 w-4" />}
            size="sm"
          >
            Boshlash
          </Button>
        )}

        {slot.status === 'in_progress' && isReviewer && (
          <Button
            onClick={onFinish}
            loading={loading}
            icon={<CheckCircle className="h-4 w-4" />}
            size="sm"
          >
            Tugatish
          </Button>
        )}

        {(slot.status === 'open' || slot.status === 'booked') && (
          <Button
            variant="danger"
            onClick={onCancel}
            loading={loading}
            icon={<XCircle className="h-4 w-4" />}
            size="sm"
          >
            Bekor qilish
          </Button>
        )}

        {slot.status === 'booked' && isReviewer && (
          <Button
            variant="secondary"
            onClick={onCancel}
            loading={loading}
            icon={<UserX className="h-4 w-4" />}
            size="sm"
          >
            Kelmadi
          </Button>
        )}
      </div>
    </Card>
  )
}

function TimelineItem({ label, time, done }: { label: string; time?: string; done?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`h-3 w-3 rounded-full shrink-0 ${
          done ? 'bg-primary-500' : 'border-2 border-gray-300 dark:border-gray-600'
        }`}
      />
      <div className="flex-1">
        <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
      </div>
      {time && <span className="text-xs text-gray-500">{time}</span>}
    </div>
  )
}
