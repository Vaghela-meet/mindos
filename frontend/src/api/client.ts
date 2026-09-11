import { Goal, Task, GoalPriority, TaskPriority, Availability, DayOfWeek } from '@/types/domain'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

async function parseError(res: Response, defaultMsg: string): Promise<string> {
  try {
    const data = await res.json()
    if (data?.detail) {
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    }
  } catch {
    // fallback
  }
  return `${defaultMsg}: ${res.statusText}`
}

export async function getGoals(): Promise<Goal[]> {
  const res = await fetch(`${API_BASE}/goals`)
  if (!res.ok) throw new Error(await parseError(res, 'Failed to fetch goals'))
  return res.json()
}

export async function createGoal(payload: {
  title: string
  description?: string
  priority?: GoalPriority
}): Promise<Goal> {
  const res = await fetch(`${API_BASE}/goals`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to create goal'))
  return res.json()
}

export async function getTasks(goalId?: number): Promise<Task[]> {
  const url = goalId ? `${API_BASE}/tasks?goal_id=${goalId}` : `${API_BASE}/tasks`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await parseError(res, 'Failed to fetch tasks'))
  return res.json()
}

export async function createTask(payload: {
  goal_id: number
  title: string
  description?: string
  priority?: TaskPriority
  estimated_minutes?: number
}): Promise<Task> {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to create task'))
  return res.json()
}

export async function updateTask(
  taskId: number,
  payload: Partial<Task>
): Promise<Task> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to update task'))
  return res.json()
}

export async function getAvailabilities(dayOfWeek?: DayOfWeek): Promise<Availability[]> {
  const url = dayOfWeek ? `${API_BASE}/availability?day_of_week=${dayOfWeek}` : `${API_BASE}/availability`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await parseError(res, 'Failed to fetch availabilities'))
  return res.json()
}

export async function createAvailability(payload: {
  day_of_week: DayOfWeek
  start_time: string
  end_time: string
}): Promise<Availability> {
  const res = await fetch(`${API_BASE}/availability`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to create availability'))
  return res.json()
}

export async function updateAvailability(
  id: number,
  payload: Partial<{
    day_of_week: DayOfWeek
    start_time: string
    end_time: string
  }>
): Promise<Availability> {
  const res = await fetch(`${API_BASE}/availability/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to update availability'))
  return res.json()
}

export async function deleteAvailability(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/availability/${id}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error(await parseError(res, 'Failed to delete availability'))
}
