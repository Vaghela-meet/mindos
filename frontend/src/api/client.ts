import { Goal, Task, GoalPriority, TaskPriority } from '@/types/domain'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export async function getGoals(): Promise<Goal[]> {
  const res = await fetch(`${API_BASE}/goals`)
  if (!res.ok) throw new Error(`Failed to fetch goals: ${res.statusText}`)
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
  if (!res.ok) throw new Error(`Failed to create goal: ${res.statusText}`)
  return res.json()
}

export async function getTasks(goalId?: number): Promise<Task[]> {
  const url = goalId ? `${API_BASE}/tasks?goal_id=${goalId}` : `${API_BASE}/tasks`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to fetch tasks: ${res.statusText}`)
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
  if (!res.ok) throw new Error(`Failed to create task: ${res.statusText}`)
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
  if (!res.ok) throw new Error(`Failed to update task: ${res.statusText}`)
  return res.json()
}
