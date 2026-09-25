export type GoalStatus = 'ACTIVE' | 'COMPLETED' | 'ARCHIVED'
export type GoalPriority = 'LOW' | 'MEDIUM' | 'HIGH'

export interface Goal {
  id: number
  user_id: number
  title: string
  description?: string | null
  status: GoalStatus
  priority: GoalPriority
  deadline?: string | null
  created_at: string
  updated_at: string
}

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH'

export type TaskType =
  | 'ROUTINE'
  | 'DEEP_WORK'
  | 'SHALLOW_WORK'
  | 'HABIT'
  | 'DEADLINE_DRIVEN'
  | 'CREATIVE'
  | 'ADMINISTRATIVE'

export type RecurrenceCadence = 'DAILY' | 'WEEKDAYS' | 'WEEKLY'

export interface Task {
  id: number
  goal_id: number
  title: string
  description?: string | null
  status: TaskStatus
  priority: TaskPriority
  task_type?: TaskType
  is_recurring?: boolean
  recurrence_cadence?: RecurrenceCadence | null
  estimated_minutes?: number | null
  deadline?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
}

export type DayOfWeek =
  | 'MONDAY'
  | 'TUESDAY'
  | 'WEDNESDAY'
  | 'THURSDAY'
  | 'FRIDAY'
  | 'SATURDAY'
  | 'SUNDAY'

export interface Availability {
  id: number
  user_id: number
  day_of_week: DayOfWeek
  start_time: string
  end_time: string
  created_at: string
  updated_at: string
}

export type PlanStatus = 'DRAFT' | 'ACTIVE' | 'SUPERSEDED' | 'CANCELLED'
export type BlockStatus = 'PLANNED' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'CANCELLED'

export type ScheduleReasonCode =
  | 'PRIMARY_FIT'
  | 'DEADLINE_PRESSURE_IMMINENT'
  | 'DEADLINE_PRESSURE_APPROACHING'
  | 'DEADLINE_PRESSURE_OVERDUE'
  | 'GOAL_ALIGNMENT_HIGH'
  | 'TASK_PRIORITY_HIGH'
  | 'CONTEXT_CONTINUITY'
  | 'TASK_IN_PROGRESS'
  | 'GAP_FILL_ROUTINE'
  | 'PARTIAL_WINDOW_SPLIT'

export type ExclusionReasonCode =
  | 'INSUFFICIENT_CAPACITY'
  | 'LOWER_PRIORITY'
  | 'WINDOW_TOO_SMALL'
  | 'DEADLINE_OUTSIDE_HORIZON'
  | 'MAX_DAILY_SPLITS_REACHED'
  | 'NO_AVAILABILITY'
  | 'NO_ACTIONABLE_TASKS'

export interface ScheduleBlock {
  id: number
  plan_id: number
  task_id: number
  task_title?: string | null
  task_type?: TaskType | null
  goal_title?: string | null
  goal_id?: number | null
  start_time: string
  end_time: string
  duration_minutes: number
  status: BlockStatus
  schedule_reason_code: ScheduleReasonCode
  created_at: string
  updated_at: string
}

export interface ShortfallRecord {
  task_id: number
  task_title: string
  unscheduled_minutes: number
  reason_code: ExclusionReasonCode
}

export interface ShortfallReport {
  total_shortfall_minutes: number
  usable_capacity_minutes: number
  records: ShortfallRecord[]
}

export interface DailyPlan {
  id: number
  user_id: number
  plan_date: string
  status: PlanStatus
  usable_capacity_minutes: number
  allocated_minutes: number
  buffer_minutes: number
  shortfall_minutes: number
  notes?: string | null
  created_at: string
  updated_at: string
  blocks: ScheduleBlock[]
  shortfall_report?: ShortfallReport | null
}
