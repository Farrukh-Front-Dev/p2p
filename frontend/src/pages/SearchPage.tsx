import { useState } from 'react'
import { Search, CalendarClock, MapPin, Monitor } from 'lucide-react'
import { useInProgressProjects, useSlotSearch, useBookSlot } from '@/hooks/use-slots'
import { Button, Card, Badge, PageLoader, EmptyState } from '@/components/ui'

export function SearchPage() {
  const [selectedProject, setSelectedProject] = useState('')
  const { data: projects, isLoading: loadingProjects } = useInProgressProjects()
  const { data: results, isLoading: searching } = useSlotSearch(selectedProject)
  const bookSlot = useBookSlot()

  const handleBook = async (slotId: string) => {
    await bookSlot.mutateAsync({ id: slotId, revieweeProject: selectedProject })
  }

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
        Slot qidirish
      </h1>

      {/* Project selection */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5 block">
              O'rganayotgan loyihangiz
            </label>
            {loadingProjects ? (
              <p className="text-sm text-gray-500">Yuklanmoqda...</p>
            ) : (
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm"
              >
                <option value="">Loyihani tanlang...</option>
                {projects?.map((p) => (
                  <option key={p.title} value={p.title}>
                    {p.title}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="flex items-end">
            <Button disabled={!selectedProject} icon={<Search className="h-4 w-4" />}>
              Qidirish
            </Button>
          </div>
        </div>
      </Card>

      {/* Results */}
      {searching ? (
        <PageLoader />
      ) : selectedProject && results?.length === 0 ? (
        <EmptyState
          icon={<Search className="h-10 w-10" />}
          title="Slot topilmadi"
          description="Bu loyiha bo'yicha hozircha ochiq slot yo'q. Keyinroq qaytib ko'ring."
        />
      ) : results && results.length > 0 ? (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">
            {results.length} ta ochiq slot topildi
          </p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((slot) => (
              <Card key={slot.id} className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <CalendarClock className="h-4 w-4 text-gray-400" />
                  {new Date(slot.start_time).toLocaleString('uz-UZ', {
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  {slot.is_online ? (
                    <Badge variant="info">
                      <Monitor className="h-3 w-3 mr-1" /> Online
                    </Badge>
                  ) : (
                    <Badge variant="default">
                      <MapPin className="h-3 w-3 mr-1" /> {slot.campus}
                    </Badge>
                  )}
                </div>
                <Button
                  size="sm"
                  className="w-full"
                  onClick={() => handleBook(slot.id)}
                  loading={bookSlot.isPending}
                >
                  Band qilish
                </Button>
              </Card>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}
