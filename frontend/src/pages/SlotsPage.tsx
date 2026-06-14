import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Filter } from 'lucide-react'
import { useSlots, useTeachableProjects, useCreateSlot } from '@/hooks/use-slots'
import { useDashboard } from '@/hooks/use-dashboard'
import { Button, Card, PageLoader, EmptyState, Input } from '@/components/ui'
import { SlotCard } from '@/components/slots/SlotCard'
import { toast } from '@/components/ui/Toast'

const createSchema = z.object({
  reviewer_project: z.string().min(1, 'Loyihani tanlang'),
  start_time: z.string().min(1, 'Vaqtni belgilang'),
  end_time: z.string().min(1, 'Tugash vaqtini belgilang'),
  is_online: z.boolean(),
})

type CreateForm = z.infer<typeof createSchema>

export function SlotsPage() {
  const [filter, setFilter] = useState<string>('')
  const [showCreate, setShowCreate] = useState(false)
  const navigate = useNavigate()

  const { data: dashboard } = useDashboard()
  const { data: slots, isLoading } = useSlots(filter ? { status: filter } : undefined)
  const { data: projects } = useTeachableProjects()
  const createSlot = useCreateSlot()

  const form = useForm<CreateForm>({
    resolver: zodResolver(createSchema),
    defaultValues: { is_online: false },
  })

  const userId = dashboard?.user.id || ''

  const onSubmit = async (data: CreateForm) => {
    await createSlot.mutateAsync({
      reviewer_project: data.reviewer_project,
      start_time: new Date(data.start_time).toISOString(),
      end_time: new Date(data.end_time).toISOString(),
      is_online: data.is_online,
    })
    setShowCreate(false)
    form.reset()
    toast.success("Slot muvaffaqiyatli yaratildi!")
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          Slotlar
        </h1>
        <Button
          onClick={() => setShowCreate(!showCreate)}
          icon={<Plus className="h-4 w-4" />}
          size="sm"
        >
          Yangi slot
        </Button>
      </div>

      {/* Create form */}
      {showCreate && (
        <Card padding="lg">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              Yangi slot yaratish
            </h3>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 block">
                Loyiha
              </label>
              <select
                {...form.register('reviewer_project')}
                className="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm"
              >
                <option value="">Loyihani tanlang...</option>
                {projects?.map((p) => (
                  <option key={p.title} value={p.title}>
                    {p.title}
                  </option>
                ))}
              </select>
              {form.formState.errors.reviewer_project && (
                <p className="text-xs text-error mt-1">
                  {form.formState.errors.reviewer_project.message}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Boshlanish"
                type="datetime-local"
                {...form.register('start_time')}
                error={form.formState.errors.start_time?.message}
              />
              <Input
                label="Tugash"
                type="datetime-local"
                {...form.register('end_time')}
                error={form.formState.errors.end_time?.message}
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                {...form.register('is_online')}
                className="h-4 w-4 rounded border-border text-primary-600"
              />
              Online (masofaviy)
            </label>

            <div className="flex gap-2">
              <Button type="submit" loading={createSlot.isPending} size="sm">
                Yaratish
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setShowCreate(false)}
              >
                Bekor
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Filter */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-gray-400" />
        {['', 'open', 'booked', 'in_progress', 'completed'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === s
                ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {s === '' ? 'Hammasi' : s === 'open' ? 'Ochiq' : s === 'booked' ? 'Band' : s === 'in_progress' ? 'Jarayonda' : 'Tugallandi'}
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <PageLoader />
      ) : !slots?.length ? (
        <EmptyState
          title="Slotlar topilmadi"
          description="Filtrni o'zgartiring yoki yangi slot yarating"
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {slots.map((slot) => (
            <SlotCard
              key={slot.id}
              slot={slot}
              userId={userId}
              onClick={() => navigate(`/slots/${slot.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
