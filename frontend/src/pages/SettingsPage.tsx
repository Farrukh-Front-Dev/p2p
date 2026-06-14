import { Settings, Sun, Moon, Monitor, Globe } from 'lucide-react'
import { Card } from '@/components/ui'
import { useThemeStore } from '@/stores/theme'

export function SettingsPage() {
  const { theme, setTheme } = useThemeStore()

  const themes = [
    { key: 'light' as const, label: 'Yorug\'', icon: Sun },
    { key: 'dark' as const, label: 'Qorong\'u', icon: Moon },
    { key: 'system' as const, label: 'Tizim', icon: Monitor },
  ]

  return (
    <div className="space-y-5 max-w-xl">
      <div className="flex items-center gap-2">
        <Settings className="h-5 w-5 text-gray-400" />
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          Sozlamalar
        </h1>
      </div>

      {/* Theme */}
      <Card>
        <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-3">
          Interfeys rangi
        </h3>
        <div className="grid grid-cols-3 gap-2">
          {themes.map((t) => (
            <button
              key={t.key}
              onClick={() => setTheme(t.key)}
              className={`flex flex-col items-center gap-2 rounded-lg border p-4 transition-all ${
                theme === t.key
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-border hover:border-border-hover'
              }`}
            >
              <t.icon
                className={`h-5 w-5 ${theme === t.key ? 'text-primary-600' : 'text-gray-400'}`}
              />
              <span className={`text-xs font-medium ${theme === t.key ? 'text-primary-700 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400'}`}>
                {t.label}
              </span>
            </button>
          ))}
        </div>
      </Card>

      {/* Language info */}
      <Card>
        <div className="flex items-center gap-2 mb-2">
          <Globe className="h-4 w-4 text-gray-400" />
          <h3 className="font-medium text-gray-900 dark:text-gray-100">
            Tillar
          </h3>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          O'qitish/o'rganish tillari Profil → Onboarding orqali o'zgartiriladi.
        </p>
      </Card>
    </div>
  )
}
