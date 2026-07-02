import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { reviewsService } from '@/features/reviews/api';
import { triggerToast } from '@/shared/stores/toast';
import { ReviewCreate } from '@/shared/types/api';

export function useReviews(userId?: string) {
  const queryClient = useQueryClient();

  const myReviewsQuery = useQuery({
    queryKey: ['reviews', 'my'],
    queryFn: reviewsService.getMyReviews,
  });

  const userReviewsQuery = useQuery({
    queryKey: ['reviews', 'user', userId],
    queryFn: () => reviewsService.getUserReviews(userId || ''),
    enabled: !!userId,
  });

  const createReviewMutation = useMutation({
    mutationFn: (payload: ReviewCreate) => reviewsService.createReview(payload),
    onSuccess: () => {
      triggerToast('Fikr-mulohaza muvaffaqiyatli yuborildi', 'success');
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['slots'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Fikr yuborishda xato yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  return {
    myReviews: myReviewsQuery.data || [],
    isLoadingMyReviews: myReviewsQuery.isLoading,
    userReviews: userReviewsQuery.data || [],
    isLoadingUserReviews: userReviewsQuery.isLoading,
    createReview: createReviewMutation.mutateAsync,
    isCreatingReview: createReviewMutation.isPending,
  };
}
export default useReviews;
