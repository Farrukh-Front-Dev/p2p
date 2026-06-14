import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AuthGuard } from '@/components/guards/AuthGuard'
import { GuestGuard } from '@/components/guards/GuestGuard'
import { AppLayout } from '@/components/layout/AppLayout'
import { PageLoader } from '@/components/ui'

// ── Lazy Pages ────────────────────────────────────────────────────────────────
const LoginPage = lazy(() => import('@/pages/LoginPage').then((m) => ({ default: m.LoginPage })))
const OnboardingPage = lazy(() => import('@/pages/OnboardingPage').then((m) => ({ default: m.OnboardingPage })))
const DashboardPage = lazy(() => import('@/pages/DashboardPage').then((m) => ({ default: m.DashboardPage })))
const SlotsPage = lazy(() => import('@/pages/SlotsPage').then((m) => ({ default: m.SlotsPage })))
const SlotDetailPage = lazy(() => import('@/pages/SlotDetailPage').then((m) => ({ default: m.SlotDetailPage })))
const SearchPage = lazy(() => import('@/pages/SearchPage').then((m) => ({ default: m.SearchPage })))
const LeaderboardPage = lazy(() => import('@/pages/LeaderboardPage').then((m) => ({ default: m.LeaderboardPage })))
const ProfilePage = lazy(() => import('@/pages/ProfilePage').then((m) => ({ default: m.ProfilePage })))
const UserProfilePage = lazy(() => import('@/pages/UserProfilePage').then((m) => ({ default: m.UserProfilePage })))
const ReviewPage = lazy(() => import('@/pages/ReviewPage').then((m) => ({ default: m.ReviewPage })))
const NotificationsPage = lazy(() => import('@/pages/NotificationsPage').then((m) => ({ default: m.NotificationsPage })))
const SettingsPage = lazy(() => import('@/pages/SettingsPage').then((m) => ({ default: m.SettingsPage })))

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>
}

export const router = createBrowserRouter([
  // Guest routes
  {
    element: <GuestGuard />,
    children: [
      {
        path: '/login',
        element: (
          <SuspenseWrapper>
            <LoginPage />
          </SuspenseWrapper>
        ),
      },
    ],
  },

  // Protected routes
  {
    element: <AuthGuard />,
    children: [
      {
        path: '/onboarding',
        element: (
          <SuspenseWrapper>
            <OnboardingPage />
          </SuspenseWrapper>
        ),
      },
      {
        element: <AppLayout />,
        children: [
          {
            path: '/dashboard',
            element: (
              <SuspenseWrapper>
                <DashboardPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/slots',
            element: (
              <SuspenseWrapper>
                <SlotsPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/slots/:id',
            element: (
              <SuspenseWrapper>
                <SlotDetailPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/search',
            element: (
              <SuspenseWrapper>
                <SearchPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/leaderboard',
            element: (
              <SuspenseWrapper>
                <LeaderboardPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/profile',
            element: (
              <SuspenseWrapper>
                <ProfilePage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/profile/:username',
            element: (
              <SuspenseWrapper>
                <UserProfilePage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/review',
            element: (
              <SuspenseWrapper>
                <ReviewPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/notifications',
            element: (
              <SuspenseWrapper>
                <NotificationsPage />
              </SuspenseWrapper>
            ),
          },
          {
            path: '/settings',
            element: (
              <SuspenseWrapper>
                <SettingsPage />
              </SuspenseWrapper>
            ),
          },
        ],
      },
    ],
  },

  // Redirect root
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
])
