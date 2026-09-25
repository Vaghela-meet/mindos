import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { WorkspaceView } from './WorkspaceView'
import * as apiClient from '@/api/client'
import { DailyPlan } from '@/types/domain'

vi.mock('@/api/client', () => ({
  getTodayPlan: vi.fn(),
  generateDailyPlan: vi.fn(),
}))

const mockDailyPlan: DailyPlan = {
  id: 42,
  user_id: 1,
  plan_date: '2026-09-25',
  status: 'ACTIVE',
  usable_capacity_minutes: 300,
  allocated_minutes: 150,
  buffer_minutes: 60,
  shortfall_minutes: 30,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  blocks: [
    {
      id: 101,
      plan_id: 42,
      task_id: 1,
      task_title: 'Architect MindOS Planning Engine',
      task_type: 'DEEP_WORK',
      goal_title: 'Master Architecture',
      goal_id: 1,
      start_time: '09:00:00',
      end_time: '10:30:00',
      duration_minutes: 90,
      status: 'PLANNED',
      schedule_reason_code: 'PRIMARY_FIT',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 102,
      plan_id: 42,
      task_id: 2,
      task_title: 'Review Alembic schema constraints & M2 bounds',
      task_type: 'SHALLOW_WORK',
      goal_title: 'Master Architecture',
      goal_id: 1,
      start_time: '10:30:00',
      end_time: '11:30:00',
      duration_minutes: 60,
      status: 'PLANNED',
      schedule_reason_code: 'PRIMARY_FIT',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ],
}

describe('WorkspaceView M3 Planning Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders initial view and triggers plan generation on button click', async () => {
    vi.mocked(apiClient.getTodayPlan).mockResolvedValue(null)
    vi.mocked(apiClient.generateDailyPlan).mockResolvedValue(mockDailyPlan)

    render(<WorkspaceView />)

    expect(screen.getByRole('button', { name: /GENERATE DAILY PLAN/i })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /GENERATE DAILY PLAN/i }))

    await waitFor(() => {
      expect(apiClient.generateDailyPlan).toHaveBeenCalledTimes(1)
      expect(screen.getByText(/STATUS: ACTIVE • 2 BLOCKS SCHEDULED/i)).toBeInTheDocument()
    })

    // Capacity text reflects 150m (2h 30m)
    expect(screen.getByText(/2h 30m of unhurried focus protected today/i)).toBeInTheDocument()
    // Slack text reflects 60m buffer (1h 0m)
    expect(screen.getByText(/1h 0m slack reserved for reflection & tea/i)).toBeInTheDocument()
  })

  it('eagerly loads existing active daily plan on mount', async () => {
    vi.mocked(apiClient.getTodayPlan).mockResolvedValue(mockDailyPlan)

    render(<WorkspaceView />)

    await waitFor(() => {
      expect(screen.getByText(/STATUS: ACTIVE • 2 BLOCKS SCHEDULED/i)).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: /REPLAN TODAY/i })).toBeInTheDocument()
  })
})
