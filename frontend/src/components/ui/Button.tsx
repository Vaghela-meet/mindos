import React from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const Button: React.FC<ButtonProps> = ({
  className,
  variant = 'primary',
  size = 'md',
  children,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-accent hover:bg-accent/90 text-accent-foreground shadow-none font-medium',
    secondary: 'bg-secondary hover:bg-muted text-secondary-foreground border border-border shadow-none',
    outline: 'border border-border hover:bg-secondary text-foreground shadow-none',
    ghost: 'hover:bg-secondary text-muted-foreground hover:text-foreground shadow-none',
  }

  const sizeStyles = {
    sm: 'h-7 px-2.5 text-xs rounded-sm',
    md: 'h-8 px-3.5 text-xs rounded-sm font-medium tracking-wide',
    lg: 'h-10 px-5 text-sm rounded-sm font-medium',
  }

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center font-sans transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent disabled:pointer-events-none disabled:opacity-40 select-none',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
