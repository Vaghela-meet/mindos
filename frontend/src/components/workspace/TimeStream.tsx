import React from 'react'

export interface TimeStreamItem {
  id: string
  time: string
  title: string
  detail?: string
  durationMinutes?: number
  isNow?: boolean
  isPast?: boolean
  isItalicBreathing?: boolean
  nowBadge?: string
}

interface TimeStreamProps {
  items?: TimeStreamItem[]
  onSelectTask?: (item: TimeStreamItem) => void
}

const DEFAULT_ITEMS: TimeStreamItem[] = [
  {
    id: 'ts-1',
    time: '08:30',
    title: 'Morning coffee & architectural orientation',
    detail: 'Completed \u00b7 45m unhurried',
    isPast: true,
  },
  {
    id: 'ts-2',
    time: '09:30',
    title: 'Architect MindOS Planning Engine',
    detail: 'Isolated core deep window \u00b7 90m protected',
    durationMinutes: 90,
    isNow: true,
    nowBadge: 'NOW',
  },
  {
    id: 'ts-3',
    time: '11:00',
    title: 'Breathing Space \u2014 30m away from screens. Walk outside.',
    detail: 'Fresh air \u00b7 Zero audio devices',
    durationMinutes: 30,
    isItalicBreathing: true,
  },
  {
    id: 'ts-4',
    time: '11:30',
    title: 'Review Alembic schema constraints & M2 bounds',
    detail: 'Low friction \u00b7 Schema ledger pinned',
    durationMinutes: 30,
  },
  {
    id: 'ts-5',
    time: '12:00',
    title: 'Desk lunch & unhurried reset',
    detail: 'Paper reading only \u00b7 Protected gap',
    durationMinutes: 120,
  },
  {
    id: 'ts-6',
    time: '14:00',
    title: 'Deep Session II: Database Index Benchmarking',
    detail: '90m \u00b7 protected reserve',
    durationMinutes: 90,
  },
]

export const TimeStream: React.FC<TimeStreamProps> = ({
  items = DEFAULT_ITEMS,
  onSelectTask,
}) => {
  return (
    <aside
      aria-label="Monday Stream"
      className="rounded-sm border border-border bg-surface/40 p-6 space-y-6 transition-colors"
    >
      {/* Stream Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border-subtle">
        <span className="text-xs font-mono font-bold tracking-wider text-foreground uppercase">
          MONDAY STREAM
        </span>
        <span className="text-[11px] font-mono text-muted-foreground/80 tracking-tight">
          6 markers &bull; 0 conflicts
        </span>
      </div>

      {/* Stream Items List */}
      <div className="space-y-5">
        {items.map((item) => {
          return (
            <div
              key={item.id}
              onClick={() => onSelectTask && onSelectTask(item)}
              className={`flex items-start space-x-4 transition-all ${
                item.isNow
                  ? 'border-l-2 border-l-accent pl-3 py-1.5 -ml-3 bg-accent/5 rounded-r-sm'
                  : 'py-0.5'
              } ${onSelectTask ? 'cursor-pointer group' : ''}`}
            >
              {/* Time Column in Monospace */}
              <div
                className={`w-12 shrink-0 text-xs font-mono tabular-nums pt-0.5 ${
                  item.isNow
                    ? 'font-bold text-accent'
                    : item.isPast
                    ? 'text-muted-foreground/60'
                    : 'text-muted-foreground'
                }`}
              >
                {item.time}
              </div>

              {/* Content Column */}
              <div className="min-w-0 flex-1 space-y-0.5">
                <div className="flex items-center space-x-2 flex-wrap gap-y-0.5">
                  <span
                    className={`text-xs tracking-tight ${
                      item.isItalicBreathing
                        ? 'font-display italic text-foreground/90 text-[13px]'
                        : item.isNow
                        ? 'font-sans font-semibold text-foreground'
                        : item.isPast
                        ? 'font-sans text-muted-foreground/75'
                        : 'font-sans text-foreground/85 group-hover:text-foreground font-medium'
                    }`}
                  >
                    {item.title}
                  </span>

                  {/* Terracotta NOW tag */}
                  {item.isNow && item.nowBadge && (
                    <span className="inline-flex items-center px-1.5 py-0.2 rounded-none bg-accent/15 border border-accent/30 text-accent font-mono text-[9px] font-bold uppercase tracking-wider">
                      {item.nowBadge}
                    </span>
                  )}
                </div>

                {item.detail && (
                  <p
                    className={`text-[11px] leading-tight ${
                      item.isNow
                        ? 'font-mono text-foreground/70'
                        : item.isPast
                        ? 'font-sans text-muted-foreground/50'
                        : 'font-sans text-muted-foreground/75'
                    }`}
                  >
                    {item.detail}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </aside>
  )
}
