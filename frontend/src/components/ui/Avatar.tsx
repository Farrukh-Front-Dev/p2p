import { clsx } from 'clsx'

interface AvatarProps {
  src?: string | null
  name?: string | null
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeStyles = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-16 w-16 text-lg',
}

function getInitials(name?: string | null): string {
  if (!name) return '?'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function Avatar({ src, name, size = 'md', className }: AvatarProps) {
  if (src) {
    return (
      <img
        src={src}
        alt={name || 'Avatar'}
        className={clsx(
          'rounded-full object-cover ring-2 ring-border',
          sizeStyles[size],
          className,
        )}
      />
    )
  }

  return (
    <div
      className={clsx(
        'inline-flex items-center justify-center rounded-full bg-primary-100 text-primary-700 font-semibold dark:bg-primary-900/40 dark:text-primary-300',
        sizeStyles[size],
        className,
      )}
      aria-label={name || 'User avatar'}
    >
      {getInitials(name)}
    </div>
  )
}
