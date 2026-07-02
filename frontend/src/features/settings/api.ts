import { api } from '@/shared/lib/axios';

export interface SettingsResponse {
  languages: string[];
  campus: string;
}

export const settingsService = {
  async getSettings(): Promise<SettingsResponse> {
    const { data } = await api.get<SettingsResponse>('/settings/');
    return data;
  },

  async updateLanguage(language: string): Promise<{ languages: string[] }> {
    const { data } = await api.patch<{ languages: string[] }>('/settings/language', { language });
    return data;
  },

  async updateTheme(theme: 'light' | 'dark'): Promise<{ theme: 'light' | 'dark' }> {
    const { data } = await api.patch<{ theme: 'light' | 'dark' }>('/settings/theme', { theme });
    return data;
  },
};
