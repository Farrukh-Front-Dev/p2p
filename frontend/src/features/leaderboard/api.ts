import { api } from '@/shared/lib/axios';
import { LeaderboardEntry } from '@/shared/types/api';

export const leaderboardService = {
  async getMostXP(): Promise<LeaderboardEntry[]> {
    const { data } = await api.get<LeaderboardEntry[]>('/leaderboard/most-xp');
    return data;
  },

  async getMostTaught(): Promise<LeaderboardEntry[]> {
    const { data } = await api.get<LeaderboardEntry[]>('/leaderboard/most-taught');
    return data;
  },

  async getMostLearned(): Promise<LeaderboardEntry[]> {
    const { data } = await api.get<LeaderboardEntry[]>('/leaderboard/most-learned');
    return data;
  },

  async getHistory(month: string, category: string): Promise<LeaderboardEntry[]> {
    const { data } = await api.get<LeaderboardEntry[]>('/leaderboard/history', {
      params: { month, category },
    });
    return data;
  },
};
