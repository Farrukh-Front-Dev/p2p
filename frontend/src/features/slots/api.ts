import { api } from '@/shared/lib/axios';
import { Slot, SlotCreate, SlotSearchResult, Project } from '@/shared/types/api';

export const slotsService = {
  async getSlots(status?: string, date?: string): Promise<Slot[]> {
    const { data } = await api.get<Slot[]>('/slots/', {
      params: { status, date },
    });
    return data;
  },

  async createSlot(payload: SlotCreate): Promise<Slot> {
    const { data } = await api.post<Slot>('/slots/', payload);
    return data;
  },

  async getSlotById(id: string): Promise<Slot> {
    const { data } = await api.get<Slot>(`/slots/${id}`);
    return data;
  },

  async cancelSlot(id: string, reason?: string): Promise<Slot> {
    const { data } = await api.delete<Slot>(`/slots/${id}`, {
      data: { reason },
    });
    return data;
  },

  async bookSlot(id: string, reviewee_project?: string): Promise<Slot> {
    const { data } = await api.post<Slot>(`/slots/${id}/book`, { reviewee_project });
    return data;
  },

  async startSlot(id: string): Promise<Slot> {
    const { data } = await api.post<Slot>(`/slots/${id}/start`);
    return data;
  },

  async finishSlot(id: string): Promise<Slot> {
    const { data } = await api.post<Slot>(`/slots/${id}/finish`);
    return data;
  },

  async absentSlot(id: string): Promise<Slot> {
    const { data } = await api.post<Slot>(`/slots/${id}/absent`);
    return data;
  },

  async searchSlots(project: string): Promise<SlotSearchResult[]> {
    const { data } = await api.get<SlotSearchResult[]>('/slots/search', {
      params: { project },
    });
    return data;
  },

  async getTeachableProjects(): Promise<{ projects: Project[] }> {
    const { data } = await api.get<{ projects: Project[] }>('/slots/my/teachable-projects');
    return data;
  },

  async getInProgressProjects(): Promise<{ projects: Project[] }> {
    const { data } = await api.get<{ projects: Project[] }>('/slots/my/in-progress-projects');
    return data;
  },
};
