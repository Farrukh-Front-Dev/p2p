import { api } from '@/shared/lib/axios';
import { Notification } from '@/shared/types/api';

export const notificationsService = {
  async getNotifications(limit: number = 20, offset: number = 0): Promise<Notification[]> {
    const { data } = await api.get<Notification[]>('/notifications/', {
      params: { limit, offset },
    });
    return data;
  },

  async markAsRead(id: string): Promise<void> {
    await api.post(`/notifications/${id}/read`);
  },

  async markAllAsRead(): Promise<void> {
    await api.post('/notifications/read-all');
  },
};
