import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'
import * as apiClient from '@/api/client'

const mockGoals = [
  {
    id: 1,
    user_id: 1,
    title: 'Master Architecture',
    description: 'Build modular monolith',
    status: 'ACTIVE' as const,
    priority: 'HIGH' as const,
    deadline: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

const mockTasks = [
  {
    id: 10,
    goal_id: 1,
    title: 'Write SQLAlchemy models',
    description: 'Define User, Goal, Task',
    status: 'TODO' as const,
    priority: 'HIGH' as const,
    estimated_minutes: 45,
    deadline: null,
    completed_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

vi.mock('@/api/client', () => ({
  getGoals: vi.fn(),
  getTasks: vi.fn(),
  createGoal: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
}))

describe('MindOS M1 App Shell', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.getGoals).mockResolvedValue(mockGoals)
    vi.mocked(apiClient.getTasks).mockResolvedValue(mockTasks)

    global.fetch = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'ok',
            app: 'MindOS',
            version: '0.1.0',
            environment: 'development',
            database: { status: 'disconnected', database: 'postgresql' },
          }),
      })
    )
  })

  it('renders application brand and M1 heading', async () => {
    render(<App />)
    expect(screen.getByText('MindOS')).toBeInTheDocument()
    expect(screen.getByText(/Goals • Tasks Management/i)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Backend Integration Status')).toBeInTheDocument()
    })
  })

  it('renders goals and displays tasks for the active goal', async () => {
    render(<App />)
    await waitFor(() => {
      const elements = screen.getAllByText('Master Architecture')
      expect(elements.length).toBeGreaterThanOrEqual(1)
    })
    await waitFor(() => {
      expect(screen.getByText('Write SQLAlchemy models')).toBeInTheDocument()
      expect(screen.getByText('45m')).toBeInTheDocument()
    })
  })

  it('provides new goal and new task action triggers', async () => {
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText('New Goal')).toBeInTheDocument()
      expect(screen.getByText('New Task')).toBeInTheDocument()
    })
  })
})
