import React, { useEffect, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Play, Pause, Check, ArrowLeft } from 'lucide-react'

export interface FocusTaskData {
  id?: string | number
  title: string
  goalTitle?: string
  durationMinutes: number
  taskType?: string
  startTime?: string
  endTime?: string
  state?: string
}

interface FocusModeViewProps {
  item: FocusTaskData
  nextItem?: FocusTaskData
  onExit: () => void
  onComplete: () => void
}

export const FocusModeView: React.FC<FocusModeViewProps> = ({
  item,
  nextItem,
  onExit,
  onComplete,
}) => {
  // Initial timer setup: 58m 21s default or calculated from duration
  const [secondsRemaining, setSecondsRemaining] = useState<number>(
    Math.min(item.durationMinutes * 60, 58 * 60 + 21)
  )
  const [isRunning, setIsRunning] = useState<boolean>(true)

  // Timer interval
  useEffect(() => {
    if (!isRunning) return
    const interval = setInterval(() => {
      setSecondsRemaining((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => clearInterval(interval)
  }, [isRunning])

  // Keyboard navigation: Escape to exit, Space to toggle pause
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onExit()
      } else if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault()
        setIsRunning((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onExit])

  // Format HH:MM:SS or MM:SS
  const formatTimer = (totalSeconds: number) => {
    const h = Math.floor(totalSeconds / 3600)
    const m = Math.floor((totalSeconds % 3600) / 60)
    const s = totalSeconds % 60
    const pad = (n: number) => n.toString().padStart(2, '0')
    return `${pad(h)} : ${pad(m)} : ${pad(s)}`
  }

  return (
    <div className="min-h-[80vh] flex flex-col justify-between py-12 px-6 max-w-4xl mx-auto transition-all animate-fadeIn">
      {/* Top Bar: Quiet exit */}
      <div className="flex items-center justify-between text-xs font-mono text-muted-foreground">
        <button
          onClick={onExit}
          className="inline-flex items-center space-x-1.5 text-muted-foreground hover:text-foreground transition-colors group"
        >
          <ArrowLeft className="h-3.5 w-3.5 group-hover:-translate-x-0.5 transition-transform" />
          <span>Workspace (Esc)</span>
        </button>

        <div className="flex items-center space-x-2 uppercase tracking-wider text-[11px]">
          <span className="h-2 w-2 rounded-full bg-accent animate-pulse" />
          <span>Focus Mode Active</span>
        </div>
      </div>

      {/* Main Focus Canvas */}
      <div className="my-auto py-16 text-center space-y-8">
        {/* Parent Goal Context */}
        {item.goalTitle && (
          <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground/80">
            Goal &bull; {item.goalTitle}
          </div>
        )}

        {/* Dominant Active Task Title */}
        <h1 className="font-display text-3xl sm:text-5xl lg:text-6xl font-medium tracking-tight text-foreground max-w-3xl mx-auto leading-tight">
          {item.title}
        </h1>

        {/* Big Serene Timer */}
        <div className="py-4">
          <div className="font-mono text-5xl sm:text-7xl lg:text-8xl font-light tracking-wider text-foreground tabular-nums select-none">
            {formatTimer(secondsRemaining)}
          </div>
          <p className="mt-3 text-xs sm:text-sm font-sans text-muted-foreground tracking-wide">
            {isRunning ? 'focused work' : 'paused'} &bull; {item.taskType?.replace('_', ' ').toLowerCase() || 'deep focus'}
          </p>
        </div>

        {/* Minimal Actions */}
        <div className="flex items-center justify-center space-x-3 pt-4">
          <Button
            variant="secondary"
            size="md"
            onClick={() => setIsRunning((prev) => !prev)}
            className="space-x-1.5 px-4 h-9"
          >
            {isRunning ? (
              <>
                <Pause className="h-3.5 w-3.5" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5" />
                <span>Resume</span>
              </>
            )}
          </Button>

          <Button
            variant="outline"
            size="md"
            onClick={onComplete}
            className="space-x-1.5 px-4 h-9 text-status-healthy hover:text-status-healthy hover:bg-status-healthy/10 hover:border-status-healthy/30"
          >
            <Check className="h-3.5 w-3.5" />
            <span>Complete Block</span>
          </Button>
        </div>
      </div>

      {/* Bottom Quiet Status: Up Next */}
      <div className="text-center pt-8 border-t border-border-subtle text-xs font-sans text-muted-foreground flex items-center justify-center space-x-2">
        {nextItem ? (
          <>
            <span className="font-mono uppercase text-[10px] tracking-wider text-muted-foreground/70">
              Next Up:
            </span>
            <span className="font-medium text-foreground/80">{nextItem.title}</span>
            {nextItem.startTime && (
              <span className="font-mono text-[10px] text-muted-foreground">({nextItem.startTime})</span>
            )}
          </>
        ) : (
          <span>No further scheduled blocks for this availability window.</span>
        )}
      </div>
    </div>
  )
}
