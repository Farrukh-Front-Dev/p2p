import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MapPin, Code2, Star } from 'lucide-react'
import { profileService } from '@/services/profile'
import { reviewService } from '@/services/reviews'
import { Card, Avatar, Badge, PageLoader, EmptyState } from '@/components/ui'

export function UserProfilePage() {
  const { username } = useParams<{ username: string }>()

  const { data: user, isLoading } = useQuery({
    queryKey: ['profile', username],
    queryFn: () => profileService.getPublic(username!),
    enabled: !!username,
  })

  const { data: reviews } = useQuery({
    queryKey: ['reviews', 'user', user?.id],
    queryFn: () => reviewService.forUser(user!.id),
    enabled: !!user?.id,
  })

  if (isLoading) return <PageLoader />
  if (!user) {
    return <EmptyState title="Foydalanuvchi topilmadi" />
  }

  const positiveCount = reviews?.filter((r) => r.is_positive).length ?? 0
  const negativeCount = reviews?.filter((r) => !r.is_positive).length ?? 0

  return (
    <div className="space-y-5 max-w-2xl">
      <Card padding="lg">
        <div className="flex items-start gap-4">
          <Avatar src={user.avatar_url} name={user.first_name} size="xl" />
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {user.first_name} {user.last_name}
            </h1>

            <div className="flex flex-wrap gap-2 mt-3">
              {user.campus && (
                <Badge variant="default">
                  <MapPin className="h-3 w-3 mr-1" /> {user.campus}
                </Badge>
              )}
              {user.main_track && (
                <Badge variant="purple">
                  <Code2 className="h-3 w-3 mr-1" /> {user.main_track}
                </Badge>
              )}
              {user.coalition_name && (
                <Badge variant="info">
                  <Star className="h-3 w-3 mr-1" /> {user.coalition_name}
                </Badge>
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <div className="grid grid-cols-3 divide-x divide-border text-center">
          <div className="py-2">
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{user.level}</p>
            <p className="text-xs text-gray-500">Level</p>
          </div>
          <div className="py-2">
            <p className="text-2xl font-bold text-emerald-600">{positiveCount}</p>
            <p className="text-xs text-gray-500">👍 Ijobiy</p>
          </div>
          <div className="py-2">
            <p className="text-2xl font-bold text-red-600">{negativeCount}</p>
            <p className="text-xs text-gray-500">👎 Salbiy</p>
          </div>
        </div>
      </Card>

      {/* Reviews list */}
      {reviews && reviews.length > 0 && (
        <Card padding="none">
          <div className="px-4 py-3 border-b border-border">
            <h3 className="font-medium text-gray-900 dark:text-gray-100">
              Sharhlar ({reviews.length})
            </h3>
          </div>
          <div className="divide-y divide-border max-h-80 overflow-y-auto">
            {reviews.map((r) => (
              <div key={r.id} className="px-4 py-3 flex items-start gap-3">
                <span className="text-lg shrink-0">
                  {r.is_positive ? '👍' : '👎'}
                </span>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {r.comment || (r.is_positive ? 'Yaxshi tajriba' : 'Yomon tajriba')}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
