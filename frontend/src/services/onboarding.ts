import api from '@/lib/axios'
import type { OnboardingStatus } from '@/types/api'

export const onboardingService = {
  getTrack: () =>
    api.get('/onboarding/track').then((r) => r.data),

  confirmTrack: (mainTrack: string) =>
    api.post('/onboarding/confirm', { main_track: mainTrack }).then((r) => r.data),

  setLanguages: (languages: string[]) =>
    api.post<OnboardingStatus>('/onboarding/languages', { languages }).then((r) => r.data),

  status: () =>
    api.get<OnboardingStatus>('/onboarding/status').then((r) => r.data),
}
