import { api } from '@/shared/lib/axios';
import { DashboardResponse } from '@/shared/types/api';

export const dashboardService = {
  async getDashboard(): Promise<DashboardResponse> {
    const { data } = await api.get<DashboardResponse>('/dashboard/');
    return data;
  },
};
