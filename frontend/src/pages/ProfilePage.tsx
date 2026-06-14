import { useQuery } from '@tanstack/react-query'
import {
  MapPin,
  Code2,
  Star,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  GraduationCap,
} from 'lucide-react'
import { profileService } from '@/services/profile'
import { Card, Avatar, Badge, PageLoader } from '@/components/ui'

export function ProfilePage() {
  const { data, isLoading } = useQuery({
    queryKey: ['profile', 'me'],
    queryFn: profileService.my,
  })

  if (isLoading) return <PageLoader />
  if (!data) return null

  const { user, stats } = data

  return (
    <div className="space-y-5 max-w-2xl">
      {/* Profile header */}
      <Card padding="lg">
        <div className="flex items-start gap-4">
          <Avatar src={user.avatar_url} name={user.first_name || user.school21_login} size="xl" />
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {user.first_name} {user.last_name}
            </h1>
            <p className="text-sm text-gray-500">@{user.school21_login}</p>

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

            {user.languages?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {user.languages.map((lang: string) => (
                  <span
                    key={lang}
                    className="px-2 py-0.5 rounded text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                  >
                    {lang}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatItem
          icon={<ThumbsUp className="h-4 w-4 text-emerald-500" />}
          label="Ijobiy"
          value={stats.positive_reviews}
        />
        <StatItem
          icon={<ThumbsDown className="h-4 w-4 text-red-500" />}
          label="Salbiy"
          value={stats.negative_reviews}
        />
        <StatItem
          icon={<BookOpen className="h-4 w-4 text-primary-500" />}
          label="O'qitgan"
          value={stats.taught_count}
        />
        <StatItem
          icon={<GraduationCap className="h-4 w-4 text-blue-500" />}
          label="O'rgangan"
          value={stats.learned_count}
        />
      </div>

      {/* Level & Points */}
      <Card>
        <div className="grid grid-cols-3 divide-x divide-border text-center">
          <div className="py-2">
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {user.level}
            </p>
            <p className="text-xs text-gray-500">Level</p>
          </div>
          <div className="py-2">
            <p className="text-2xl font-bold text-primary-600">{user.peer_points}</p>
            <p className="text-xs text-gray-500">Peer Points</p>
          </div>
          <div className="py-2">
            <p className="text-2xl font-bold text-emerald-600">{user.peer_coins}</p>
            <p className="text-xs text-gray-500">Peer Coins</p>
          </div>
        </div>
      </Card>
    </div>
  )
}

function StatItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: number
}) {
  return (
    <Card className="flex items-center gap-3">
      {icon}
      <div>
        <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{value}</p>
        <p className="text-xs text-gray-500">{label}</p>
      </div>
    </Card>
  )
}
