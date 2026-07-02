import { api } from '@/shared/lib/axios';
import { UserMe, UserPublic, ProfileStats } from '@/shared/types/api';

export interface MyProfileResponse {
  user: UserMe;
  stats: ProfileStats;
}

/** School21 skill yozuvi: nomi + xom ballari */
export interface Skill {
  name: string;
  points: number;
}

export const profileService = {
  async getMyProfile(): Promise<MyProfileResponse> {
    const { data } = await api.get<MyProfileResponse>('/profile/');
    return data;
  },

  async updateProfile(payload: {
    first_name?: string;
    last_name?: string;
    avatar_url?: string;
  }): Promise<UserMe> {
    const { data } = await api.patch<UserMe>('/profile/', payload);
    return data;
  },

  async getSkills(): Promise<Skill[]> {
    const { data } = await api.get<{ skills: Skill[] }>('/profile/skills');
    return data.skills || [];
  },

  async getPublicProfile(username: string): Promise<UserPublic> {
    const { data } = await api.get<UserPublic>(`/profile/${username}`);
    return data;
  },
};
