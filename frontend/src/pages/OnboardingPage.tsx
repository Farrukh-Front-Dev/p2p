import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, ChevronRight, Languages } from 'lucide-react'
import { Button, Card, Badge } from '@/components/ui'
import { onboardingService } from '@/services/onboarding'
import { useAuthStore } from '@/stores/auth'

const AVAILABLE_LANGUAGES = [
  'O\'zbek', 'Русский', 'English', 'Français', 'Deutsch',
  'Español', 'Türkçe', 'العربية', 'فارسی', '中文',
]

export function OnboardingPage() {
  const navigate = useNavigate()
  const setOnboardingDone = useAuthStore((s) => s.setOnboardingDone)

  const [step, setStep] = useState<'track' | 'languages'>('track')
  const [selectedTrack, setSelectedTrack] = useState('')
  const [selectedLangs, setSelectedLangs] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const { data: trackData } = useQuery({
    queryKey: ['onboarding', 'track'],
    queryFn: onboardingService.getTrack,
  })

  const tracks = ['Web', 'Mobile', 'GameDev', 'DataScience', 'DevOps', 'Blockchain']

  const handleConfirmTrack = async () => {
    if (!selectedTrack) return
    setLoading(true)
    try {
      await onboardingService.confirmTrack(selectedTrack)
      setStep('languages')
    } finally {
      setLoading(false)
    }
  }

  const toggleLang = (lang: string) => {
    setSelectedLangs((prev) =>
      prev.includes(lang) ? prev.filter((l) => l !== lang) : [...prev, lang],
    )
  }

  const handleFinish = async () => {
    if (selectedLangs.length === 0) return
    setLoading(true)
    try {
      await onboardingService.setLanguages(selectedLangs)
      setOnboardingDone(true)
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950 p-4">
      <div className="w-full max-w-lg">
        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className={`h-2 w-16 rounded-full ${step === 'track' ? 'bg-primary-500' : 'bg-primary-500'}`} />
          <div className={`h-2 w-16 rounded-full ${step === 'languages' ? 'bg-primary-500' : 'bg-gray-200 dark:bg-gray-700'}`} />
        </div>

        <Card padding="lg">
          {step === 'track' ? (
            <div className="space-y-5">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Asosiy yo'nalishingiz
                </h2>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {trackData?.core_program
                    ? `Core: ${trackData.core_program}. Asosiy track ni tanlang.`
                    : 'Asosiy o\'qitish yo\'nalishingizni tanlang'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {tracks.map((track) => (
                  <button
                    key={track}
                    onClick={() => setSelectedTrack(track)}
                    className={`flex items-center justify-between rounded-lg border px-4 py-3 text-sm font-medium transition-all ${
                      selectedTrack === track
                        ? 'border-primary-500 bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                        : 'border-border text-gray-700 dark:text-gray-300 hover:border-border-hover'
                    }`}
                  >
                    {track}
                    {selectedTrack === track && <CheckCircle2 className="h-4 w-4" />}
                  </button>
                ))}
              </div>

              <Button
                onClick={handleConfirmTrack}
                className="w-full"
                disabled={!selectedTrack}
                loading={loading}
                icon={<ChevronRight className="h-4 w-4" />}
              >
                Davom etish
              </Button>
            </div>
          ) : (
            <div className="space-y-5">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  Tillar
                </h2>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  O'qitish/o'rganish uchun qaysi tillarni bilasiz?
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                {AVAILABLE_LANGUAGES.map((lang) => (
                  <button
                    key={lang}
                    onClick={() => toggleLang(lang)}
                    className="transition-all"
                  >
                    <Badge
                      variant={selectedLangs.includes(lang) ? 'purple' : 'default'}
                    >
                      <Languages className="h-3 w-3 mr-1" />
                      {lang}
                    </Badge>
                  </button>
                ))}
              </div>

              <Button
                onClick={handleFinish}
                className="w-full"
                disabled={selectedLangs.length === 0}
                loading={loading}
              >
                Boshlash 🚀
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
