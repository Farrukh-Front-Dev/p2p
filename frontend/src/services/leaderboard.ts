import api from '@/lib/axios'
import type { LeaderboardEntry } from '@/types/api'

export const leaderboardService = {
  mostTaught: () =>
    api.get<LeaderboardEntry[]>('/leaderboard/most-taught').then((r) => r.data),

  mostLearned: () =>
    api.get<LeaderboardEntry[]>('/leaderboard/most-learned').then((r) => r.data),

  mostXp: () =>
    api.get<LeaderboardEntry[]>('/leaderboard/most-xp').then((r) => r.data),
}
