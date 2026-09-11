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

export interface Task {
  id: number
  goal_id: number
  title: string
  description?: string | null
  status: TaskStatus
  priority: TaskPriority
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
