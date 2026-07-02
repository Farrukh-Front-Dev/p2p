import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import { triggerToast } from '@/shared/stores/toast';
import { LoginRequest, VerifyCodeRequest } from '@/shared/types/api';

export function useAuth() {
  const queryClient = useQueryClient();
  const { setTokens, logout, isAuthenticated } = useAuthStore();

  const meQuery = useQuery({
    queryKey: ['me'],
    queryFn: authService.me,
    enabled: isAuthenticated,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: (payload: LoginRequest) => authService.login(payload),
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || "Login yoki parol noto'g'ri";
      triggerToast(detail, 'error');
    },
  });

  const verifyCodeMutation = useMutation({
    mutationFn: (payload: VerifyCodeRequest) => authService.verifyCode(payload),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token, data.onboarding_done);
      queryClient.invalidateQueries({ queryKey: ['me'] });
      triggerToast('Muvaffaqiyatli kirdingiz!', 'success');
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Kod noto‘g‘ri yoki muddati o‘tgan';
      triggerToast(detail, 'error');
    },
  });

  const unlinkTelegramMutation = useMutation({
    mutationFn: (password: string) => authService.unlinkTelegram(password),
    onSuccess: () => {
      triggerToast('Telegram akkounti muvaffaqiyatli uzildi.', 'success');
      queryClient.invalidateQueries({ queryKey: ['me'] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Parol noto‘g‘ri';
      triggerToast(detail, 'error');
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSettled: () => {
      logout();
      queryClient.clear();
      triggerToast('Tizimdan chiqdingiz', 'info');
    },
  });

  return {
    user: meQuery.data,
    isLoadingUser: meQuery.isLoading,
    isErrorUser: meQuery.isError,
    login: loginMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    loginData: loginMutation.data,
    verifyCode: verifyCodeMutation.mutate,
    isVerifyingCode: verifyCodeMutation.isPending,
    unlinkTelegram: unlinkTelegramMutation.mutate,
    isUnlinkingTelegram: unlinkTelegramMutation.isPending,
    logout: logoutMutation.mutate,
  };
}
