import api from '@/lib/axios'
import type { ProfileUpdate, UserMe, UserPublic } from '@/types/api'

export const profileService = {
  my: () => api.get('/profile/').then((r) => r.data),

  update: (data: ProfileUpdate) =>
    api.patch<UserMe>('/profile/', data).then((r) => r.data),

  skills: () => api.get('/profile/skills').then((r) => r.data),

  getPublic: (username: string) =>
    api.get<UserPublic>(`/profile/${username}`).then((r) => r.data),
}
