import React, { useState } from 'react'
import { Play, Check } from 'lucide-react'

export interface Checkpoint {
  id: string
  text: string
  completed: boolean
}

interface DeskSheetProps {
  time?: string
  docReference?: string
  goalTitle?: string
  taskTitle?: string
  taskDescription?: string
  durationMinutes?: number
  energyWindow?: string
  checkpoints?: Checkpoint[]
  onBeginSession: () => void
}

export const DeskSheet: React.FC<DeskSheetProps> = ({
  time = '09:30 AM',
  docReference = 'GOAL-01 // ARCHITECTURE-CORE',
  taskTitle = 'Architect MindOS Planning Engine',
  taskDescription = 'Refactor task prioritization model & slot allocation contracts before architecture review. Formalize discrete window-aware boundaries without duration-inferred task classification.',
  durationMinutes = 90,
  energyWindow = 'deep energy window',
  checkpoints: initialCheckpoints = [
    { id: 'cp-1', text: 'Define discrete availability slot runs without flattening gaps', completed: true },
    { id: 'cp-2', text: 'Isolate pure deterministic scheduling loop from database persistence', completed: false },
    { id: 'cp-3', text: 'Verify shortfall accounting & structured exclusion reasons', completed: false },
  ],
  onBeginSession,
}) => {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>(initialCheckpoints)

  const toggleCheckpoint = (id: string) => {
    setCheckpoints((prev) =>
      prev.map((cp) => (cp.id === id ? { ...cp, completed: !cp.completed } : cp))
    )
  }

  return (
    <article
      aria-label="Current Living Desk Sheet"
      className="relative rounded-sm border border-border bg-surface/75 p-6 sm:p-8 transition-colors shadow-[0_1px_3px_rgba(0,0,0,0.03)]"
    >
      {/* Top Metadata Strip */}
      <div className="flex items-center justify-between pb-4 border-b border-border-subtle text-[11px] font-mono uppercase tracking-wider text-muted-foreground">
        <div className="flex items-center space-x-2 text-accent font-medium">
          <span className="h-2 w-2 rounded-full bg-accent" />
          <span>CURRENT MOMENT &bull; {time}</span>
        </div>

        <div className="text-muted-foreground/80 tracking-widest text-[10px]">
          [{docReference}]
        </div>
      </div>

      {/* Energy Window / Duration Tag */}
      <div className="pt-5">
        <span className="inline-flex items-center px-2 py-0.5 rounded-sm border border-border text-[11px] font-mono text-muted-foreground bg-surface-muted/50">
          <span className="mr-1.5 opacity-60">&bull;</span>
          <span>{durationMinutes} minutes allocated &bull; {energyWindow}</span>
        </span>
      </div>

      {/* Dominant Task Title in Newsreader Editorial Serif */}
      <div className="pt-3 space-y-3">
        <h2 className="font-display text-2xl sm:text-3xl lg:text-[2.25rem] font-medium tracking-tight text-foreground leading-[1.2]">
          {taskTitle}
        </h2>

        {taskDescription && (
          <p className="font-sans text-xs sm:text-sm text-foreground/80 leading-relaxed max-w-2xl">
            {taskDescription}
          </p>
        )}
      </div>

      {/* Manuscript Scope / Checkpoints */}
      {checkpoints.length > 0 && (
        <div className="pt-6 space-y-3">
          <div className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground/80 font-medium">
            MANUSCRIPT SCOPE
          </div>
          <div className="space-y-2">
            {checkpoints.map((cp, idx) => (
              <button
                key={cp.id}
                onClick={() => toggleCheckpoint(cp.id)}
                className="w-full text-left flex items-start space-x-3 group py-0.5 focus-visible:outline-none"
              >
                {/* Custom square box matching Stitch styling */}
                <div
                  className={`mt-0.5 h-3.5 w-3.5 shrink-0 rounded-none border flex items-center justify-center transition-colors text-[10px] ${
                    cp.completed
                      ? 'border-foreground/80 bg-foreground/10 text-foreground'
                      : idx === 1
                      ? 'border-accent bg-accent/15 text-accent'
                      : 'border-border group-hover:border-foreground/60'
                  }`}
                >
                  {cp.completed ? (
                    <Check className="h-2.5 w-2.5 stroke-[2.5]" />
                  ) : idx === 1 ? (
                    <span className="h-1.5 w-1.5 bg-accent rounded-none" />
                  ) : null}
                </div>
                <span
                  className={`text-xs font-sans tracking-tight transition-colors ${
                    cp.completed
                      ? 'line-through text-muted-foreground'
                      : 'text-foreground/90 group-hover:text-foreground'
                  }`}
                >
                  {cp.text}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Action Strip */}
      <div className="pt-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-t border-border-subtle mt-6">
        <div className="text-xs font-mono text-muted-foreground/75 tracking-tight flex items-center space-x-2">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent/60" />
          <span>Protected focus state ready &bull; Zero external distractions</span>
        </div>

        {/* Primary Terracotta Begin Session Button */}
        <button
          onClick={onBeginSession}
          aria-label="Start Focus Session"
          className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-sm bg-accent hover:bg-accent/90 text-accent-foreground font-mono text-xs font-medium uppercase tracking-wider transition-colors shadow-none select-none"
        >
          <Play className="h-3 w-3 fill-current" />
          <span>[ BEGIN SESSION ]</span>
        </button>
      </div>
    </article>
  )
}
