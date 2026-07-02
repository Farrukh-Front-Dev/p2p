import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { profileService } from '@/features/profile/api';
import { triggerToast } from '@/shared/stores/toast';

export function useProfile(username?: string) {
  const queryClient = useQueryClient();

  const myProfileQuery = useQuery({
    queryKey: ['profile', 'me'],
    queryFn: profileService.getMyProfile,
  });

  const publicProfileQuery = useQuery({
    queryKey: ['profile', 'public', username],
    queryFn: () => profileService.getPublicProfile(username || ''),
    enabled: !!username,
  });

  const skillsQuery = useQuery({
    queryKey: ['profile', 'skills'],
    queryFn: profileService.getSkills,
  });

  const updateProfileMutation = useMutation({
    mutationFn: (payload: { first_name?: string; last_name?: string; avatar_url?: string }) =>
      profileService.updateProfile(payload),
    onSuccess: (updatedUser) => {
      triggerToast('Profil muvaffaqiyatli yangilandi', 'success');
      queryClient.setQueryData(['me'], updatedUser);
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || 'Profilni yangilashda xatolik yuz berdi';
      triggerToast(detail, 'error');
    },
  });

  return {
    profile: myProfileQuery.data,
    isLoadingProfile: myProfileQuery.isLoading,

    publicProfile: publicProfileQuery.data,
    isLoadingPublicProfile: publicProfileQuery.isLoading,

    skills: skillsQuery.data || [],
    isLoadingSkills: skillsQuery.isLoading,

    updateProfile: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
  };
}
export default useProfile;
