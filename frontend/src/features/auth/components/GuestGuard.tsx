import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store';
import { ReactNode } from 'react';

interface GuestGuardProps {
  children: ReactNode;
}

export function GuestGuard({ children }: GuestGuardProps) {
  const { isAuthenticated, onboardingDone } = useAuthStore();

  if (isAuthenticated) {
    if (!onboardingDone) {
      return <Navigate to="/onboarding" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
export default GuestGuard;
