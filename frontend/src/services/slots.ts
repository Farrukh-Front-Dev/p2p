import api from '@/lib/axios'
import type { Slot, SlotCreate, SlotSearchResult, Project } from '@/types/api'

export const slotService = {
  list: (params?: { status?: string; date?: string }) =>
    api.get<Slot[]>('/slots/', { params }).then((r) => r.data),

  get: (id: string) => api.get<Slot>(`/slots/${id}`).then((r) => r.data),

  create: (data: SlotCreate) =>
    api.post<Slot>('/slots/', data).then((r) => r.data),

  cancel: (id: string, reason?: string) =>
    api.delete<Slot>(`/slots/${id}`, { data: { reason } }).then((r) => r.data),

  book: (id: string, revieweeProject?: string) =>
    api
      .post<Slot>(`/slots/${id}/book`, { reviewee_project: revieweeProject })
      .then((r) => r.data),

  start: (id: string) =>
    api.post<Slot>(`/slots/${id}/start`).then((r) => r.data),

  finish: (id: string) =>
    api.post<Slot>(`/slots/${id}/finish`).then((r) => r.data),

  markAbsent: (id: string) =>
    api.post<Slot>(`/slots/${id}/absent`).then((r) => r.data),

  search: (project: string) =>
    api
      .get<SlotSearchResult[]>('/slots/search', { params: { project } })
      .then((r) => r.data),

  teachableProjects: () =>
    api
      .get<{ projects: Project[] }>('/slots/my/teachable-projects')
      .then((r) => r.data.projects),

  inProgressProjects: () =>
    api
      .get<{ projects: Project[] }>('/slots/my/in-progress-projects')
      .then((r) => r.data.projects),
}
