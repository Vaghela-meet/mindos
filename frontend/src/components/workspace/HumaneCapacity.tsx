import React from 'react'

interface HumaneCapacityProps {
  protectedFocusText?: string
  slackText?: string
}

export const HumaneCapacity: React.FC<HumaneCapacityProps> = ({
  protectedFocusText = '4h 20m of unhurried focus protected today',
  slackText = 'Breathing room protected \u00b7 1h 45m slack reserved for reflection & tea',
}) => {
  return (
    <section
      aria-label="Humane Capacity & Rhythm"
      className="rounded-sm border border-border bg-surface/40 p-5 transition-colors"
    >
      {/* Top Header Text Strip */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-3">
        <div className="flex items-center space-x-2">
          <span className="h-2 w-2 rounded-full bg-accent shrink-0" />
          <h3 className="font-display text-base sm:text-lg font-medium text-foreground tracking-tight">
            {protectedFocusText}
          </h3>
        </div>

        <div className="text-[11px] font-mono text-muted-foreground/80 tracking-tight">
          {slackText}
        </div>
      </div>

      {/* Segmented Timeline Track */}
      <div className="pt-2">
        <div className="h-2 w-full bg-surface-muted rounded-none overflow-hidden flex gap-[2px]">
          {/* Morning Deep Work (09:00 - 11:00) */}
          <div
            className="h-full bg-accent transition-all"
            style={{ width: '38%' }}
            title="09:00 - 11:00: Morning Deep Focus"
          />
          {/* Rest / Walk (11:00 - 12:00) */}
          <div
            className="h-full bg-muted transition-all"
            style={{ width: '16%' }}
            title="11:00 - 12:00: Rest & Reflection"
          />
          {/* Lunch (12:00 - 14:00) */}
          <div
            className="h-full bg-secondary border-x border-border-subtle transition-all"
            style={{ width: '14%' }}
            title="12:00 - 14:00: Midday Reset & Lunch"
          />
          {/* Afternoon Depth (14:00 - 16:30) */}
          <div
            className="h-full bg-foreground/60 transition-all"
            style={{ width: '24%' }}
            title="14:00 - 16:30: Afternoon Depth"
          />
          {/* Desk Clear (16:30 - 17:00) */}
          <div
            className="h-full bg-muted/60 transition-all"
            style={{ width: '8%' }}
            title="17:00: Desk Clear"
          />
        </div>

        {/* Timeline Coordinates matching Stitch reference */}
        <div className="flex items-center justify-between pt-2 text-[10px] font-mono uppercase tracking-wider text-muted-foreground/75">
          <span>09:00 START</span>
          <span>11:00 REST / WALK</span>
          <span>12:00 LUNCH</span>
          <span>14:00 AFTERNOON DEPTH</span>
          <span>17:00 DESK CLEAR</span>
        </div>
      </div>
    </section>
  )
}
