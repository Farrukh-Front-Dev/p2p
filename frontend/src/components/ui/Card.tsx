import { type HTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

const paddingStyles = {
  none: '',
  sm: 'p-3',
  md: 'p-4 sm:p-5',
  lg: 'p-5 sm:p-6',
}

export function Card({
  padding = 'md',
  hover = false,
  children,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-border bg-surface shadow-sm',
        paddingStyles[padding],
        hover && 'transition-shadow hover:shadow-md cursor-pointer',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}
