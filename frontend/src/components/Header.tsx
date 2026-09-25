import React, { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'

interface HeaderProps {
  activeTab?: 'workspace' | 'goals' | 'availability'
  onSelectTab?: (tab: 'workspace' | 'goals' | 'availability') => void
  onTriggerFocus?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  activeTab = 'workspace',
  onSelectTab,
  onTriggerFocus,
}) => {
  const [isDark, setIsDark] = useState<boolean>(true)
  const [currentTime, setCurrentTime] = useState<string>('08:24 PM')

  // Theme toggle initialization
  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains('dark')
    setIsDark(isDarkMode)
  }, [])

  // Live system clock formatted like Stitch (HH:MM AM/PM)
  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      let hours = now.getHours()
      const ampm = hours >= 12 ? 'PM' : 'AM'
      hours = hours % 12 || 12
      const minutes = now.getMinutes().toString().padStart(2, '0')
      setCurrentTime(`${hours.toString().padStart(2, '0')}:${minutes} ${ampm}`)
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark')
      setIsDark(false)
    } else {
      document.documentElement.classList.add('dark')
      setIsDark(true)
    }
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
        {/* Left Side: Brand, Navigation, Time */}
        <div className="flex items-center space-x-6">
          <div className="flex items-baseline space-x-1.5">
            <span className="font-display text-xl font-bold tracking-tight text-foreground select-none">
              MindOS
            </span>
          </div>

          {/* Navigation with Stitch-style active underline */}
          {onSelectTab && (
            <nav className="flex items-center space-x-6" aria-label="Primary Navigation">
              <button
                onClick={() => onSelectTab('workspace')}
                className={`text-xs font-mono tracking-wider uppercase transition-colors relative py-1 ${
                  activeTab === 'workspace'
                    ? 'text-foreground font-semibold after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-accent'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                WORKSPACE
              </button>

              <button
                onClick={() => onSelectTab('goals')}
                className={`text-xs font-mono tracking-wider uppercase transition-colors relative py-1 ${
                  activeTab === 'goals'
                    ? 'text-foreground font-semibold after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-accent'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                GOALS &bull; TASKS
              </button>

              <button
                onClick={() => onSelectTab('availability')}
                className={`text-xs font-mono tracking-wider uppercase transition-colors relative py-1 ${
                  activeTab === 'availability'
                    ? 'text-foreground font-semibold after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-accent'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                WEEKLY AVAILABILITY
              </button>
            </nav>
          )}

          {/* System Time Coordinate */}
          <div className="hidden md:block text-[11px] font-mono text-muted-foreground/80 pl-2">
            {currentTime}
          </div>
        </div>

        {/* Right Side: Theme Switcher & Focus Mode Button */}
        <div className="flex items-center space-x-3">
          {/* Light / Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            aria-label={isDark ? 'Switch to Light paper mode' : 'Switch to Dark charcoal mode'}
            className="p-1.5 rounded-sm text-muted-foreground hover:text-foreground hover:bg-surface transition-colors"
            title={isDark ? 'Light mode (Warm paper)' : 'Dark mode (Charcoal)'}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          {/* Stitch Focus Button */}
          {onTriggerFocus && (
            <button
              onClick={onTriggerFocus}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-sm bg-foreground hover:bg-foreground/90 text-background font-mono text-xs font-medium tracking-wide transition-colors select-none"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
              <span>&bull; Focus</span>
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
