import { Component, type ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button, Card } from '@/components/ui'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="flex min-h-[50vh] items-center justify-center p-4">
          <Card padding="lg" className="max-w-md text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-amber-500 mb-4" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Xatolik yuz berdi
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {this.state.error?.message || 'Kutilmagan xatolik. Sahifani yangilang.'}
            </p>
            <div className="flex gap-2 justify-center">
              <Button
                onClick={this.handleReset}
                variant="secondary"
                icon={<RefreshCw className="h-4 w-4" />}
              >
                Qayta urinish
              </Button>
              <Button onClick={() => window.location.reload()}>
                Sahifani yangilash
              </Button>
            </div>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
