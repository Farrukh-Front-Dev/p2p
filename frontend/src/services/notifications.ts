import api from '@/lib/axios'
import type { Notification } from '@/types/api'

export const notificationService = {
  list: (params?: { limit?: number; offset?: number }) =>
    api.get<Notification[]>('/notifications/', { params }).then((r) => r.data),

  markRead: (id: string) => api.post(`/notifications/${id}/read`),

  markAllRead: () => api.post('/notifications/read-all'),
}
