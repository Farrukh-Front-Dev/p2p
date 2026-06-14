import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '@/stores/auth'
import { useQueryClient } from '@tanstack/react-query'

export function useSlotWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const { accessToken, isAuthenticated } = useAuthStore()
  const qc = useQueryClient()

  const connect = useCallback(() => {
    if (!accessToken || !isAuthenticated) return

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${window.location.host}/ws/slots?token=${accessToken}`

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'slot_update') {
          qc.invalidateQueries({ queryKey: ['slots'] })
          qc.invalidateQueries({ queryKey: ['dashboard'] })
        }
        if (msg.type === 'notification') {
          qc.invalidateQueries({ queryKey: ['notifications'] })
          qc.invalidateQueries({ queryKey: ['dashboard'] })
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      // Reconnect after 3s
      setTimeout(connect, 3000)
    }
  }, [accessToken, isAuthenticated, qc])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])
}
