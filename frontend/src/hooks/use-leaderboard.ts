import { useQuery } from '@tanstack/react-query'
import { leaderboardService } from '@/services/leaderboard'

export function useMostTaught() {
  return useQuery({
    queryKey: ['leaderboard', 'most-taught'],
    queryFn: leaderboardService.mostTaught,
    staleTime: 60_000,
  })
}

export function useMostLearned() {
  return useQuery({
    queryKey: ['leaderboard', 'most-learned'],
    queryFn: leaderboardService.mostLearned,
    staleTime: 60_000,
  })
}

export function useMostXp() {
  return useQuery({
    queryKey: ['leaderboard', 'most-xp'],
    queryFn: leaderboardService.mostXp,
    staleTime: 60_000,
  })
}
