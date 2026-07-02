import { api } from '@/shared/lib/axios';
import { LoginRequest, LoginResponse, VerifyCodeRequest, TokenResponse, UserMe } from '@/shared/types/api';

export const authService = {
  async login(payload: LoginRequest): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>('/auth/login', payload);
    return data;
  },

  async verifyCode(payload: VerifyCodeRequest): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/verify-code', payload);
    return data;
  },

  async unlinkTelegram(password: string): Promise<void> {
    await api.post('/auth/unlink-telegram', { password });
  },

  async me(): Promise<UserMe> {
    const { data } = await api.get<UserMe>('/auth/me');
    return data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },
};
