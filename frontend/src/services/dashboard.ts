import api from '@/lib/axios'
import type { DashboardResponse } from '@/types/api'

export const dashboardService = {
  get: () => api.get<DashboardResponse>('/dashboard/').then((r) => r.data),
}
