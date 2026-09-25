import React from 'react'

interface MorningNoteProps {
  note?: string
  timestamp?: string
}

export const MorningNote: React.FC<MorningNoteProps> = ({
  note = 'The queue can wait until noon. Today calls for depth on the planning engine architecture and nothing more. Two meetings have been softly deferred to Wednesday.',
  timestamp = '08:45',
}) => {
  return (
    <aside
      aria-label="Desk Note"
      className="rounded-sm border border-border bg-surface/60 p-5 transition-colors shadow-[0_1px_2px_rgba(0,0,0,0.02)]"
    >
      {/* Desk Note Monospace Header */}
      <div className="flex items-center justify-between pb-2 text-[10px] font-mono uppercase tracking-widest text-muted-foreground/80 font-medium">
        <span>[DESK NOTE // {timestamp}]</span>
        <span className="h-1.5 w-1.5 rounded-full bg-accent/70" />
      </div>

      {/* Desk Note Text */}
      <p className="font-sans text-xs sm:text-sm text-foreground/85 leading-relaxed tracking-tight">
        {note}
      </p>
    </aside>
  )
}
