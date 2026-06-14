import api from '@/lib/axios'
import type { Review, ReviewCreate } from '@/types/api'

export const reviewService = {
  create: (data: ReviewCreate) =>
    api.post<Review>('/reviews/', data).then((r) => r.data),

  my: () => api.get<Review[]>('/reviews/my').then((r) => r.data),

  forUser: (userId: string) =>
    api.get<Review[]>(`/reviews/user/${userId}`).then((r) => r.data),
}
