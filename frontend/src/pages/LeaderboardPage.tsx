import { useState } from 'react'
import { Trophy, BookOpen, GraduationCap, Zap } from 'lucide-react'
import { useMostTaught, useMostLearned, useMostXp } from '@/hooks/use-leaderboard'
import { Card, Avatar, Badge, PageLoader } from '@/components/ui'
import type { LeaderboardEntry } from '@/types/api'

type Tab = 'xp' | 'taught' | 'learned'

const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
  { key: 'xp', label: 'XP', icon: <Zap className="h-4 w-4" /> },
  { key: 'taught', label: "O'qitgan", icon: <BookOpen className="h-4 w-4" /> },
  { key: 'learned', label: "O'rgangan", icon: <GraduationCap className="h-4 w-4" /> },
]

export function LeaderboardPage() {
  const [tab, setTab] = useState<Tab>('xp')
  const { data: xpData, isLoading: loadXp } = useMostXp()
  const { data: taughtData, isLoading: loadTaught } = useMostTaught()
  const { data: learnedData, isLoading: loadLearned } = useMostLearned()

  const dataMap: Record<Tab, LeaderboardEntry[] | undefined> = {
    xp: xpData,
    taught: taughtData,
    learned: learnedData,
  }

  const isLoading = tab === 'xp' ? loadXp : tab === 'taught' ? loadTaught : loadLearned
  const entries = dataMap[tab] || []

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Trophy className="h-6 w-6 text-amber-500" />
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          Reyting taxtasi
        </h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              tab === t.key
                ? 'bg-surface text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <PageLoader />
      ) : (
        <Card padding="none">
          <div className="divide-y divide-border">
            {entries.map((entry, idx) => (
              <div
                key={entry.id}
                className="flex items-center gap-4 px-4 py-3 sm:px-5"
              >
                {/* Rank */}
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 font-bold text-sm shrink-0">
                  {idx < 3 ? (
                    <span className={idx === 0 ? 'text-amber-500' : idx === 1 ? 'text-gray-400' : 'text-orange-500'}>
                      {idx + 1}
                    </span>
                  ) : (
                    <span className="text-gray-500">{idx + 1}</span>
                  )}
                </div>

                {/* Avatar + Name */}
                <Avatar
                  src={entry.avatar_url}
                  name={entry.first_name || entry.school21_login}
                  size="sm"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {entry.first_name} {entry.last_name}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    @{entry.school21_login}
                  </p>
                </div>

                {/* Score */}
                <Badge variant="purple">
                  {tab === 'xp' ? `${entry.xp} XP` : `${entry.count ?? 0}`}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
