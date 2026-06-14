import api from '@/lib/axios'
import type {
  LoginRequest,
  LoginResponse,
  TokenResponse,
  VerifyCodeRequest,
} from '@/types/api'

export const authService = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data).then((r) => r.data),

  verifyCode: (data: VerifyCodeRequest) =>
    api.post<TokenResponse>('/auth/verify-code', data).then((r) => r.data),

  refresh: (refreshToken: string) =>
    api
      .post<TokenResponse>('/auth/refresh', { refresh_token: refreshToken })
      .then((r) => r.data),

  logout: () => api.post('/auth/logout'),

  me: () => api.get('/auth/me').then((r) => r.data),
}
