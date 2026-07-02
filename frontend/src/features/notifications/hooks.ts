import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { notificationsService } from '@/features/notifications/api';
import { triggerToast } from '@/shared/stores/toast';

export function useNotifications() {
  const queryClient = useQueryClient();

  const notificationsQuery = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsService.getNotifications(50, 0),
  });

  const markOneReadMutation = useMutation({
    mutationFn: (id: string) => notificationsService.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Amal bajarilmadi';
      triggerToast(detail, 'error');
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: notificationsService.markAllAsRead,
    onSuccess: () => {
      triggerToast('Barcha bildirishnomalar o‘qildi deb belgilandi', 'success');
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Amal bajarilmadi';
      triggerToast(detail, 'error');
    },
  });

  return {
    notifications: notificationsQuery.data || [],
    isLoading: notificationsQuery.isLoading,
    markAsRead: markOneReadMutation.mutateAsync,
    isMarkingAsRead: markOneReadMutation.isPending,
    markAllAsRead: markAllReadMutation.mutateAsync,
    isMarkingAllAsRead: markAllReadMutation.isPending,
  };
}
export default useNotifications;
