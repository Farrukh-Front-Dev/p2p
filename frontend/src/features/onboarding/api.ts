import { api } from '@/shared/lib/axios';
import { OnboardingStatus } from '@/shared/types/api';

export interface OnboardingTrackResponse {
  core_program: string | null;
  main_track: string | null;
}

export const onboardingService = {
  async getTrack(): Promise<OnboardingTrackResponse> {
    const { data } = await api.get<OnboardingTrackResponse>('/onboarding/track');
    return data;
  },

  async confirmTrack(main_track: string): Promise<OnboardingTrackResponse> {
    const { data } = await api.post<OnboardingTrackResponse>('/onboarding/confirm', { main_track });
    return data;
  },

  async confirmLanguages(languages: string[]): Promise<OnboardingStatus> {
    const { data } = await api.post<OnboardingStatus>('/onboarding/languages', { languages });
    return data;
  },

  async getStatus(): Promise<OnboardingStatus> {
    const { data } = await api.get<OnboardingStatus>('/onboarding/status');
    return data;
  },
};
