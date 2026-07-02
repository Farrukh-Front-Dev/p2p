import { useQuery } from '@tanstack/react-query';
import { leaderboardService } from '@/features/leaderboard/api';

export function useLeaderboard() {
  const mostXPQuery = useQuery({
    queryKey: ['leaderboard', 'most-xp'],
    queryFn: leaderboardService.getMostXP,
  });

  const mostTaughtQuery = useQuery({
    queryKey: ['leaderboard', 'most-taught'],
    queryFn: leaderboardService.getMostTaught,
  });

  const mostLearnedQuery = useQuery({
    queryKey: ['leaderboard', 'most-learned'],
    queryFn: leaderboardService.getMostLearned,
  });

  return {
    mostXP: mostXPQuery.data || [],
    isLoadingXP: mostXPQuery.isLoading,
    isErrorXP: mostXPQuery.isError,

    mostTaught: mostTaughtQuery.data || [],
    isLoadingTaught: mostTaughtQuery.isLoading,
    isErrorTaught: mostTaughtQuery.isError,

    mostLearned: mostLearnedQuery.data || [],
    isLoadingLearned: mostLearnedQuery.isLoading,
    isErrorLearned: mostLearnedQuery.isError,

    refetchXP: mostXPQuery.refetch,
    refetchTaught: mostTaughtQuery.refetch,
    refetchLearned: mostLearnedQuery.refetch,
  };
}
export default useLeaderboard;
