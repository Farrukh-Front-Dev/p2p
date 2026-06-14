import { useEffect, useState, useCallback } from 'react'
import { clsx } from 'clsx'
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react'
import { create } from 'zustand'

/* ── Toast Store ──────────────────────────────────────────────────────────────── */
type ToastType = 'success' | 'error' | 'info'

interface ToastItem {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastStore {
  toasts: ToastItem[]
  add: (type: ToastType, message: string, duration?: number) => void
  remove: (id: string) => void
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  add: (type, message, duration = 4000) => {
    const id = crypto.randomUUID()
    set((s) => ({ toasts: [...s.toasts, { id, type, message, duration }] }))
  },
  remove: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

/** Helper to call toast from anywhere */
export const toast = {
  success: (msg: string) => useToastStore.getState().add('success', msg),
  error: (msg: string) => useToastStore.getState().add('error', msg),
  info: (msg: string) => useToastStore.getState().add('info', msg),
}

/* ── Toast Item Component ─────────────────────────────────────────────────────── */
function ToastItemView({ item, onDismiss }: { item: ToastItem; onDismiss: () => void }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true))
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onDismiss, 200)
    }, item.duration ?? 4000)
    return () => clearTimeout(timer)
  }, [item.duration, onDismiss])

  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle2 className="h-5 w-5 text-emerald-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <Info className="h-5 w-5 text-blue-500" />,
  }

  return (
    <div
      className={clsx(
        'flex items-center gap-3 rounded-lg border border-border bg-surface px-4 py-3 shadow-lg transition-all duration-200',
        visible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0',
      )}
      role="alert"
    >
      {icons[item.type]}
      <p className="flex-1 text-sm text-gray-800 dark:text-gray-200">{item.message}</p>
      <button
        onClick={() => { setVisible(false); setTimeout(onDismiss, 200) }}
        className="shrink-0 rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

/* ── Toast Container (render once in App) ─────────────────────────────────────── */
export function ToastContainer() {
  const { toasts, remove } = useToastStore()

  const handleDismiss = useCallback(
    (id: string) => remove(id),
    [remove],
  )

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-4 right-4 z-100 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
      aria-live="polite"
    >
      {toasts.map((t) => (
        <div key={t.id} className="pointer-events-auto">
          <ToastItemView item={t} onDismiss={() => handleDismiss(t.id)} />
        </div>
      ))}
    </div>
  )
}
