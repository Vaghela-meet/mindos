import React, { useState, useEffect } from 'react'
import { MorningNote } from './MorningNote'
import { HumaneCapacity } from './HumaneCapacity'
import { DeskSheet } from './DeskSheet'
import { TimeStream, TimeStreamItem } from './TimeStream'
import { FocusModeView } from './FocusModeView'
import { DailyPlan } from '@/types/domain'
import { getTodayPlan, generateDailyPlan } from '@/api/client'
import { RefreshCw } from 'lucide-react'

interface WorkspaceViewProps {
  onStartFocusDirectly?: () => void
}

export const WorkspaceView: React.FC<WorkspaceViewProps> = () => {
  const [plan, setPlan] = useState<DailyPlan | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  const [focusedTask, setFocusedTask] = useState<{
    title: string
    goalTitle?: string
    durationMinutes: number
    taskType: string
  } | null>(null)

  // Fetch today's plan on mount
  useEffect(() => {
    let mounted = true
    getTodayPlan()
      .then((p) => {
        if (mounted && p) {
          setPlan(p)
        }
      })
      .catch(() => {
        // Fallback gracefully to visual defaults
      })
    return () => {
      mounted = false
    }
  }, [])

  const handleGeneratePlan = async () => {
    setIsGenerating(true)
    setGenerateError(null)
    try {
      const newPlan = await generateDailyPlan()
      setPlan(newPlan)
    } catch (err: any) {
      setGenerateError(err?.message || 'Failed to generate plan')
    } finally {
      setIsGenerating(false)
    }
  }

  // Derive active task from plan if available, else fallback to visual baseline
  const activeTask =
    plan && plan.blocks && plan.blocks.length > 0
      ? {
          title: plan.blocks[0].task_title || 'Active Commitment',
          goalTitle: plan.blocks[0].goal_title || 'Primary Goal',
          durationMinutes: plan.blocks[0].duration_minutes,
          taskType: plan.blocks[0].task_type || 'DEEP_WORK',
          docReference: plan.blocks[0].goal_title
            ? `GOAL // ${plan.blocks[0].goal_title.toUpperCase()}`
            : 'GOAL-01 // ARCHITECTURE-CORE',
          description: `Scheduled via deterministic planner (${plan.blocks[0].schedule_reason_code.replace(/_/g, ' ').toLowerCase()}). Continuous 30m grid allocation.`,
        }
      : {
          title: 'Architect MindOS Planning Engine',
          goalTitle: 'Master Architecture',
          durationMinutes: 90,
          taskType: 'DEEP WORK',
          docReference: 'GOAL-01 // ARCHITECTURE-CORE',
          description:
            'Refactor task prioritization model & slot allocation contracts before architecture review. Formalize discrete window-aware boundaries without duration-inferred task classification.',
        }

  // Next scheduled task
  const nextTask =
    plan && plan.blocks && plan.blocks.length > 1
      ? {
          title: plan.blocks[1].task_title || 'Next Session',
          startTime: plan.blocks[1].start_time.slice(0, 5),
        }
      : {
          title: 'Review Alembic schema constraints & M2 bounds',
          startTime: '11:30 AM',
        }

  // Derive stream items from plan if available
  const streamItems: TimeStreamItem[] | undefined =
    plan && plan.blocks && plan.blocks.length > 0
      ? plan.blocks.map((b, idx) => ({
          id: `block-${b.id}`,
          time: b.start_time.slice(0, 5),
          title: b.task_title || `Focus Session ${idx + 1}`,
          detail: `${b.task_type || 'WORK'} · ${b.duration_minutes}m · ${b.schedule_reason_code.replace(/_/g, ' ').toLowerCase()}`,
          durationMinutes: b.duration_minutes,
          isNow: idx === 0,
          nowBadge: idx === 0 ? 'NOW' : undefined,
        }))
      : undefined

  // Derive capacity texts from plan if available
  const protectedFocusText =
    plan && plan.allocated_minutes > 0
      ? `${Math.floor(plan.allocated_minutes / 60)}h ${plan.allocated_minutes % 60}m of unhurried focus protected today`
      : '4h 20m of unhurried focus protected today'

  const slackText =
    plan && plan.buffer_minutes > 0
      ? `Breathing room protected • ${Math.floor(plan.buffer_minutes / 60)}h ${plan.buffer_minutes % 60}m slack reserved for reflection & tea`
      : 'Breathing room protected • 1h 45m slack reserved for reflection & tea'

  if (focusedTask) {
    return (
      <FocusModeView
        item={{
          id: 'focus-active',
          startTime: '09:30',
          endTime: '11:00',
          durationMinutes: focusedTask.durationMinutes,
          title: focusedTask.title,
          goalTitle: focusedTask.goalTitle,
          taskType: 'DEEP_WORK',
          state: 'NOW',
        }}
        nextItem={{
          id: 'focus-next',
          startTime: nextTask.startTime,
          endTime: '12:00',
          durationMinutes: 30,
          title: nextTask.title,
          taskType: 'SHALLOW_WORK',
          state: 'UPCOMING',
        }}
        onExit={() => setFocusedTask(null)}
        onComplete={() => setFocusedTask(null)}
      />
    )
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16 transition-colors">
      {/* ================================================== */}
      {/* 1. ARRIVAL & DESK NOTE (TOP VIEWPORT)              */}
      {/* ================================================== */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-2 sm:pt-4">
        {/* Left Side: Editorial Arrival */}
        <div className="lg:col-span-8 space-y-3">
          {/* Metadata tracking line in JetBrains Mono */}
          <div className="text-[11px] font-mono tracking-widest text-muted-foreground uppercase flex items-center space-x-2">
            <span>MON &bull; 24 SEPTEMBER &bull; WEEK 39 &bull; Quiet Monday cadence active</span>
          </div>

          {/* Large Editorial Serif Greeting */}
          <h1 className="font-display text-4xl sm:text-5xl lg:text-[3.25rem] font-normal tracking-tight text-foreground lowercase leading-[1.1]">
            good morning, meetraj.
          </h1>

          {/* Calming human subtitle */}
          <p className="font-display italic text-base sm:text-lg text-muted-foreground leading-relaxed pt-0.5">
            you don&apos;t have to solve the whole day yet.
          </p>

          {/* Plan Status / Regenerate action button */}
          <div className="pt-2 flex items-center space-x-4">
            <button
              onClick={handleGeneratePlan}
              disabled={isGenerating}
              className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-sm border border-border bg-surface hover:bg-surface-muted text-xs font-mono tracking-wider uppercase text-muted-foreground hover:text-foreground transition-all duration-150 disabled:opacity-50"
            >
              <RefreshCw className={`h-3 w-3 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>{isGenerating ? 'CALCULATING PLAN...' : plan ? 'REPLAN TODAY' : 'GENERATE DAILY PLAN'}</span>
            </button>
            {plan && (
              <span className="text-[11px] font-mono text-muted-foreground/80 tracking-wider uppercase">
                STATUS: {plan.status} &bull; {plan.blocks.length} BLOCKS SCHEDULED
              </span>
            )}
            {generateError && (
              <span className="text-[11px] font-mono text-accent">
                {generateError}
              </span>
            )}
          </div>
        </div>

        {/* Right Side: Tactile Desk Note */}
        <div className="lg:col-span-4">
          <MorningNote
            timestamp="08:45"
            note="The queue can wait until noon. Today calls for depth on the planning engine architecture and nothing more. Two meetings have been softly deferred to Wednesday."
          />
        </div>
      </section>

      {/* ================================================== */}
      {/* 2. HUMANE CAPACITY & DAY RHYTHM TRACK               */}
      {/* ================================================== */}
      <HumaneCapacity
        protectedFocusText={protectedFocusText}
        slackText={slackText}
      />

      {/* ================================================== */}
      {/* 3. LIVING DESK: ACTIVE DESK SHEET & MONDAY STREAM   */}
      {/* ================================================== */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start pt-2">
        {/* Left Column: Living Document on the Desk */}
        <div className="lg:col-span-7">
          <DeskSheet
            time="09:30 AM"
            docReference={activeTask.docReference}
            goalTitle={activeTask.goalTitle}
            taskTitle={activeTask.title}
            taskDescription={activeTask.description}
            durationMinutes={activeTask.durationMinutes}
            energyWindow="deep energy window"
            onBeginSession={() => setFocusedTask(activeTask)}
          />
        </div>

        {/* Right Column: Monday Stream */}
        <div className="lg:col-span-5">
          <TimeStream
            items={streamItems}
            onSelectTask={(item: TimeStreamItem) => {
              if (item.isNow) {
                setFocusedTask(activeTask)
              }
            }}
          />
        </div>
      </section>
    </div>
  )
}
