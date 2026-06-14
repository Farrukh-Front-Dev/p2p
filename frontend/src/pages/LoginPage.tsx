import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { LogIn, ExternalLink, KeyRound } from 'lucide-react'
import { Button, Input, Card } from '@/components/ui'
import { authService } from '@/services/auth'
import { useAuthStore } from '@/stores/auth'

const loginSchema = z.object({
  login: z.string().min(1, 'Login kiritilishi shart'),
  password: z.string().min(1, 'Parol kiritilishi shart'),
})

const codeSchema = z.object({
  code: z.string().min(4, 'Kodni kiriting'),
})

type LoginForm = z.infer<typeof loginSchema>
type CodeForm = z.infer<typeof codeSchema>

export function LoginPage() {
  const navigate = useNavigate()
  const { setTokens, setOnboardingDone } = useAuthStore()

  const [step, setStep] = useState<'login' | 'telegram'>('login')
  const [tempToken, setTempToken] = useState('')
  const [botUrl, setBotUrl] = useState<string | null>(null)
  const [error, setError] = useState('')

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const codeForm = useForm<CodeForm>({
    resolver: zodResolver(codeSchema),
  })

  const onLogin = async (data: LoginForm) => {
    setError('')
    try {
      const res = await authService.login(data)
      if (res.status === 'ok' && res.access_token && res.refresh_token) {
        setTokens(res.access_token, res.refresh_token)
        setOnboardingDone(res.onboarding_done)
        navigate(res.onboarding_done ? '/dashboard' : '/onboarding')
      } else if (res.status === 'need_telegram') {
        setTempToken(res.temp_token || '')
        setBotUrl(res.bot_url || null)
        setStep('telegram')
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Xatolik yuz berdi"
      setError(msg)
    }
  }

  const onVerify = async (data: CodeForm) => {
    setError('')
    try {
      const res = await authService.verifyCode({
        temp_token: tempToken,
        code: data.code,
      })
      setTokens(res.access_token, res.refresh_token)
      setOnboardingDone(res.onboarding_done)
      navigate(res.onboarding_done ? '/dashboard' : '/onboarding')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Kod noto'g'ri"
      setError(msg)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950 p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 h-14 w-14 rounded-2xl bg-primary-600 flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xl">P2P</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Peer Learn
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            School21 peer-to-peer o'qitish platformasi
          </p>
        </div>

        <Card padding="lg">
          {step === 'login' ? (
            <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Kirish
              </h2>

              <Input
                label="School21 login"
                placeholder="your_login"
                {...loginForm.register('login')}
                error={loginForm.formState.errors.login?.message}
              />

              <Input
                label="Parol"
                type="password"
                placeholder="••••••••"
                {...loginForm.register('password')}
                error={loginForm.formState.errors.password?.message}
              />

              {error && (
                <p className="text-sm text-error bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <Button
                type="submit"
                className="w-full"
                loading={loginForm.formState.isSubmitting}
                icon={<LogIn className="h-4 w-4" />}
              >
                Kirish
              </Button>
            </form>
          ) : (
            <form onSubmit={codeForm.handleSubmit(onVerify)} className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Telegram tasdiqlash
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Telegram botga o'ting va kodni oling
              </p>

              {botUrl && (
                <a
                  href={botUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full h-10 rounded-lg border border-border text-sm font-medium text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  Telegram botni ochish
                </a>
              )}

              <Input
                label="OTP kod"
                placeholder="123456"
                {...codeForm.register('code')}
                error={codeForm.formState.errors.code?.message}
              />

              {error && (
                <p className="text-sm text-error bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <Button
                type="submit"
                className="w-full"
                loading={codeForm.formState.isSubmitting}
                icon={<KeyRound className="h-4 w-4" />}
              >
                Tasdiqlash
              </Button>

              <button
                type="button"
                onClick={() => {
                  setStep('login')
                  setError('')
                }}
                className="w-full text-center text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                ← Loginiga qaytish
              </button>
            </form>
          )}
        </Card>
      </div>
    </div>
  )
}
