import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { slotsService } from '@/features/slots/api';
import { triggerToast } from '@/shared/stores/toast';
import { SlotCreate } from '@/shared/types/api';

export function useSlots(status?: string, date?: string) {
  const queryClient = useQueryClient();

  const slotsQuery = useQuery({
    queryKey: ['slots', { status, date }],
    queryFn: () => slotsService.getSlots(status, date),
  });

  const teachableQuery = useQuery({
    queryKey: ['teachable-projects'],
    queryFn: slotsService.getTeachableProjects,
  });

  const inProgressQuery = useQuery({
    queryKey: ['in-progress-projects'],
    queryFn: slotsService.getInProgressProjects,
  });

  const invalidateClient = () => {
    queryClient.invalidateQueries({ queryKey: ['slots'] });
    queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    queryClient.invalidateQueries({ queryKey: ['notifications'] });
  };

  const createSlotMutation = useMutation({
    mutationFn: (payload: SlotCreate) => slotsService.createSlot(payload),
    onSuccess: () => {
      triggerToast('Slot muvaffaqiyatli yaratildi', 'success');
      invalidateClient();
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Slot yaratishda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  const bookSlotMutation = useMutation({
    mutationFn: ({ id, project }: { id: string; project?: string }) =>
      slotsService.bookSlot(id, project),
    onSuccess: () => {
      triggerToast('Slot muvaffaqiyatli band qilindi', 'success');
      invalidateClient();
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Slotni band qilishda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  const startSlotMutation = useMutation({
    mutationFn: (id: string) => slotsService.startSlot(id),
    onSuccess: (updatedSlot) => {
      triggerToast('Siz tomonlama dars boshlandi', 'success');
      invalidateClient();
      queryClient.invalidateQueries({ queryKey: ['slot', updatedSlot.id] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Darsni boshlashda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  const finishSlotMutation = useMutation({
    mutationFn: (id: string) => slotsService.finishSlot(id),
    onSuccess: (updatedSlot) => {
      triggerToast('Dars muvaffaqiyatli yakunlandi', 'success');
      invalidateClient();
      queryClient.invalidateQueries({ queryKey: ['slot', updatedSlot.id] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Darsni yakunlashda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  const cancelSlotMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      slotsService.cancelSlot(id, reason),
    onSuccess: (updatedSlot) => {
      triggerToast('Slot muvaffaqiyatli bekor qilindi', 'info');
      invalidateClient();
      queryClient.invalidateQueries({ queryKey: ['slot', updatedSlot.id] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Slotni bekor qilishda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  const absentSlotMutation = useMutation({
    mutationFn: (id: string) => slotsService.absentSlot(id),
    onSuccess: (updatedSlot) => {
      triggerToast('Sherik kelmadi deb belgilandi', 'info');
      invalidateClient();
      queryClient.invalidateQueries({ queryKey: ['slot', updatedSlot.id] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Amalni bajarishda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  return {
    slots: slotsQuery.data || [],
    isLoadingSlots: slotsQuery.isLoading,
    isErrorSlots: slotsQuery.isError,
    refetchSlots: slotsQuery.refetch,

    teachableProjects: teachableQuery.data?.projects || [],
    isLoadingTeachable: teachableQuery.isLoading,

    inProgressProjects: inProgressQuery.data?.projects || [],
    isLoadingInProgress: inProgressQuery.isLoading,

    createSlot: createSlotMutation.mutateAsync,
    isCreatingSlot: createSlotMutation.isPending,

    bookSlot: bookSlotMutation.mutateAsync,
    isBookingSlot: bookSlotMutation.isPending,

    startSlot: startSlotMutation.mutateAsync,
    isStartingSlot: startSlotMutation.isPending,

    finishSlot: finishSlotMutation.mutateAsync,
    isFinishingSlot: finishSlotMutation.isPending,

    cancelSlot: cancelSlotMutation.mutateAsync,
    isCancellingSlot: cancelSlotMutation.isPending,

    absentSlot: absentSlotMutation.mutateAsync,
    isAbsentingSlot: absentSlotMutation.isPending,
  };
}
export default useSlots;
