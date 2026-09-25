import React from 'react'
import { cn } from '@/lib/utils'

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?:
    | 'default'
    | 'accent'
    | 'success'
    | 'healthy'
    | 'warning'
    | 'attention'
    | 'risk'
    | 'adaptation'
    | 'secondary'
    | 'outline'
    | 'mono'
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'default',
  children,
  ...props
}) => {
  const variantStyles: Record<string, string> = {
    default: 'bg-secondary text-foreground border-border',
    accent: 'bg-accent/10 text-accent border-accent/30 font-medium',
    success: 'bg-status-healthy/10 text-status-healthy border-status-healthy/30',
    healthy: 'bg-status-healthy/10 text-status-healthy border-status-healthy/30',
    warning: 'bg-status-attention/10 text-status-attention border-status-attention/30',
    attention: 'bg-status-attention/10 text-status-attention border-status-attention/30',
    risk: 'bg-status-risk/10 text-status-risk border-status-risk/30 font-medium',
    adaptation: 'bg-status-adaptation/10 text-status-adaptation border-status-adaptation/30 font-mono tracking-wide',
    secondary: 'bg-secondary text-secondary-foreground border-border',
    outline: 'border-border text-muted-foreground bg-transparent',
    mono: 'font-mono text-[10px] tracking-wider uppercase bg-secondary text-muted-foreground border-border',
  }

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-sm border px-2 py-0.5 text-xs font-normal transition-colors select-none',
        variantStyles[variant] || variantStyles.default,
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
