import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
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

const mockAvailabilities = [
  {
    id: 101,
    user_id: 1,
    day_of_week: 'MONDAY' as const,
    start_time: '09:00:00',
    end_time: '12:00:00',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 102,
    user_id: 1,
    day_of_week: 'MONDAY' as const,
    start_time: '14:00:00',
    end_time: '18:00:00',
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
  getAvailabilities: vi.fn(),
  createAvailability: vi.fn(),
  updateAvailability: vi.fn(),
  deleteAvailability: vi.fn(),
  getTodayPlan: vi.fn(),
  generateDailyPlan: vi.fn(),
}))

describe('MindOS Living Desk & App Shell', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.getGoals).mockResolvedValue(mockGoals)
    vi.mocked(apiClient.getTasks).mockResolvedValue(mockTasks)
    vi.mocked(apiClient.getAvailabilities).mockResolvedValue(mockAvailabilities)
    vi.mocked(apiClient.getTodayPlan).mockResolvedValue(null)
    vi.mocked(apiClient.generateDailyPlan).mockResolvedValue({
      id: 1,
      user_id: 1,
      plan_date: '2026-09-25',
      status: 'ACTIVE',
      usable_capacity_minutes: 300,
      allocated_minutes: 90,
      buffer_minutes: 60,
      shortfall_minutes: 0,
      blocks: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })

    global.fetch = vi.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'ok',
            app: 'MindOS',
            version: '0.1.0',
            environment: 'development',
            database: { status: 'connected', database: 'postgresql' },
          }),
      })
    )
  })

  it('renders application brand, editorial arrival, and living desk sheet', () => {
    render(<App />)
    expect(screen.getByText('MindOS')).toBeInTheDocument()
    expect(screen.getByText(/good morning, meetraj\./i)).toBeInTheDocument()
    expect(screen.getByText(/24 September/i)).toBeInTheDocument()
    expect(screen.getAllByText(/Architect MindOS Planning Engine/i).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/\[ BEGIN SESSION \]/i)).toBeInTheDocument()
  })

  it('renders humane capacity breathing room and Monday stream without telemetry formulas', () => {
    render(<App />)
    expect(screen.getByText(/4h 20m of unhurried focus protected today/i)).toBeInTheDocument()
    expect(screen.getByText(/MONDAY STREAM/i)).toBeInTheDocument()
    expect(screen.getByText(/DESK NOTE/i)).toBeInTheDocument()
    // Verify internal telemetry jargon is not present
    expect(screen.queryByText(/RAW AVAILABLE/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/30M GRID/i)).not.toBeInTheDocument()
  })

  it('enters Focus Mode when session is initiated and returns to workspace on exit', () => {
    render(<App />)
    const startButton = screen.getByRole('button', { name: /Start Focus Session/i })
    fireEvent.click(startButton)

    // Verify Focus Mode is active
    expect(screen.getByText(/Focus Mode Active/i)).toBeInTheDocument()
    expect(screen.getByText(/focused work/i)).toBeInTheDocument()
    expect(screen.getByText(/Pause/i)).toBeInTheDocument()

    // Click Workspace (Esc) to return
    const exitButton = screen.getByRole('button', { name: /Workspace \(Esc\)/i })
    fireEvent.click(exitButton)

    // Back in Living Desk
    expect(screen.getByText(/good morning, meetraj\./i)).toBeInTheDocument()
  })

  it('navigates to Goals & Tasks tab and displays goals and tasks', async () => {
    render(<App />)
    const goalsTabButton = screen.getByRole('button', { name: /GOALS • TASKS/i })
    fireEvent.click(goalsTabButton)

    expect(screen.getByText(/Goals & Tasks Management/i)).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Backend Integration Status')).toBeInTheDocument()
    })

    await waitFor(() => {
      const elements = screen.getAllByText('Master Architecture')
      expect(elements.length).toBeGreaterThanOrEqual(1)
    })
    await waitFor(() => {
      expect(screen.getByText('Write SQLAlchemy models')).toBeInTheDocument()
      expect(screen.getByText('45m')).toBeInTheDocument()
    })
  })

  it('navigates to Weekly Availability tab and displays availability windows', async () => {
    render(<App />)
    const availabilityTabButton = screen.getByRole('button', { name: /WEEKLY AVAILABILITY/i })
    fireEvent.click(availabilityTabButton)

    await waitFor(() => {
      expect(screen.getByText('Weekly Availability Capacity')).toBeInTheDocument()
      expect(screen.getByText('Weekly Work Capacity')).toBeInTheDocument()
      expect(screen.getByText('7h / week')).toBeInTheDocument()
    })

    // Verify Monday windows are displayed
    expect(screen.getByText('09:00 – 12:00')).toBeInTheDocument()
    expect(screen.getByText('14:00 – 18:00')).toBeInTheDocument()
  })
})
