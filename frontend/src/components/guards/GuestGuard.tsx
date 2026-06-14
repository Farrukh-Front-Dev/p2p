import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'

export function GuestGuard() {
  const { isAuthenticated, onboardingDone } = useAuthStore()

  if (isAuthenticated) {
    return <Navigate to={onboardingDone ? '/dashboard' : '/onboarding'} replace />
  }

  return <Outlet />
}
