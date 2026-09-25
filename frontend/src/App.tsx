import React, { useEffect, useState } from 'react'
import { Header } from '@/components/Header'
import { HealthCheck } from '@/components/HealthCheck'
import { GoalsView } from '@/components/goals/GoalsView'
import { TasksView } from '@/components/tasks/TasksView'
import { AvailabilityView } from '@/components/availability/AvailabilityView'
import { WorkspaceView } from '@/components/workspace/WorkspaceView'
import { Goal, Task, GoalPriority, TaskPriority, Availability, DayOfWeek } from '@/types/domain'
import {
  getGoals,
  createGoal,
  getTasks,
  createTask,
  updateTask,
  getAvailabilities,
  createAvailability,
  updateAvailability,
  deleteAvailability,
} from '@/api/client'

interface AppProps {
  initialTab?: 'workspace' | 'goals' | 'availability'
}

export const App: React.FC<AppProps> = ({ initialTab = 'workspace' }) => {
  const [activeTab, setActiveTab] = useState<'workspace' | 'goals' | 'availability'>(initialTab)

  // M1 Goals & Tasks state
  const [goals, setGoals] = useState<Goal[]>([])
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loadingGoals, setLoadingGoals] = useState<boolean>(false)
  const [loadingTasks, setLoadingTasks] = useState<boolean>(false)

  // M2 Availability state
  const [availabilities, setAvailabilities] = useState<Availability[]>([])
  const [loadingAvailabilities, setLoadingAvailabilities] = useState<boolean>(false)

  // Load goals on mount
  const loadGoals = async () => {
    setLoadingGoals(true)
    try {
      const data = await getGoals()
      setGoals(data)
      if (data.length > 0 && selectedGoalId === null) {
        setSelectedGoalId(data[0].id)
      }
    } catch {
      // Backend may be offline during standalone frontend test runs
    } finally {
      setLoadingGoals(false)
    }
  }

  // Load tasks when selected goal changes
  const loadTasks = async (goalId: number) => {
    setLoadingTasks(true)
    try {
      const data = await getTasks(goalId)
      setTasks(data)
    } catch {
      setTasks([])
    } finally {
      setLoadingTasks(false)
    }
  }

  // Load availability
  const loadAvailabilities = async () => {
    setLoadingAvailabilities(true)
    try {
      const data = await getAvailabilities()
      setAvailabilities(data)
    } catch {
      // Backend may be offline during standalone frontend test runs
    } finally {
      setLoadingAvailabilities(false)
    }
  }

  useEffect(() => {
    loadGoals()
    loadAvailabilities()
  }, [])

  useEffect(() => {
    if (selectedGoalId !== null) {
      loadTasks(selectedGoalId)
    } else {
      setTasks([])
    }
  }, [selectedGoalId])

  const handleCreateGoal = async (payload: {
    title: string
    description?: string
    priority: GoalPriority
  }) => {
    const created = await createGoal(payload)
    setGoals((prev) => [created, ...prev])
    setSelectedGoalId(created.id)
  }

  const handleCreateTask = async (payload: {
    goal_id: number
    title: string
    description?: string
    priority?: TaskPriority
    estimated_minutes?: number
  }) => {
    const created = await createTask(payload)
    setTasks((prev) => [...prev, created])
  }

  const handleToggleComplete = async (task: Task) => {
    const nextStatus = task.status === 'COMPLETED' ? 'TODO' : 'COMPLETED'
    const updated = await updateTask(task.id, { status: nextStatus })
    setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)))
  }

  // M2 Availability handlers
  const handleCreateAvailability = async (payload: {
    day_of_week: DayOfWeek
    start_time: string
    end_time: string
  }) => {
    const created = await createAvailability(payload)
    setAvailabilities((prev) => [...prev, created])
  }

  const handleUpdateAvailability = async (
    id: number,
    payload: Partial<{
      day_of_week: DayOfWeek
      start_time: string
      end_time: string
    }>
  ) => {
    const updated = await updateAvailability(id, payload)
    setAvailabilities((prev) => prev.map((a) => (a.id === id ? updated : a)))
  }

  const handleDeleteAvailability = async (id: number) => {
    await deleteAvailability(id)
    setAvailabilities((prev) => prev.filter((a) => a.id !== id))
  }

  const selectedGoal = goals.find((g) => g.id === selectedGoalId) || null

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans transition-colors duration-200">
      <Header activeTab={activeTab} onSelectTab={setActiveTab} />

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
        {/* Living Workspace (Primary Experience) */}
        {activeTab === 'workspace' && <WorkspaceView />}

        {/* Goals & Tasks View (M1 Milestone) */}
        {activeTab === 'goals' && (
          <div className="space-y-6">
            <div className="border-b border-border/80 pb-4">
              <div className="text-[11px] font-mono uppercase tracking-wider text-muted-foreground">
                MindOS &bull; Milestone 1 Primitives
              </div>
              <h1 className="font-display text-2xl sm:text-3xl font-medium text-foreground tracking-tight mt-1">
                Goals &amp; Tasks Management
              </h1>
              <p className="text-xs text-muted-foreground mt-0.5">
                Execution primitives for MindOS. Tasks belong strictly to high-level Goals with conservative deletion.
              </p>
            </div>

            <HealthCheck />

            <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5">
                <GoalsView
                  goals={goals}
                  selectedGoalId={selectedGoalId}
                  onSelectGoal={setSelectedGoalId}
                  onCreateGoal={handleCreateGoal}
                  loading={loadingGoals}
                />
              </div>

              <div className="lg:col-span-7">
                <TasksView
                  selectedGoal={selectedGoal}
                  tasks={tasks}
                  onCreateTask={handleCreateTask}
                  onToggleComplete={handleToggleComplete}
                  loading={loadingTasks}
                />
              </div>
            </section>
          </div>
        )}

        {/* Weekly Availability View (M2 Milestone) */}
        {activeTab === 'availability' && (
          <div className="space-y-6">
            <div className="border-b border-border/80 pb-4">
              <div className="text-[11px] font-mono uppercase tracking-wider text-muted-foreground">
                MindOS &bull; Milestone 2 Capacity
              </div>
              <h1 className="font-display text-2xl sm:text-3xl font-medium text-foreground tracking-tight mt-1">
                Weekly Availability Capacity
              </h1>
              <p className="text-xs text-muted-foreground mt-0.5">
                Configurable weekly working capacity. Represents when you are generally available to execute planned tasks.
              </p>
            </div>

            <HealthCheck />

            <section>
              <AvailabilityView
                availabilities={availabilities}
                onCreate={handleCreateAvailability}
                onUpdate={handleUpdateAvailability}
                onDelete={handleDeleteAvailability}
                loading={loadingAvailabilities}
              />
            </section>
          </div>
        )}
      </main>

      {/* Editorial System Footer */}
      <footer className="border-t border-border/70 py-6 text-center text-xs font-mono text-muted-foreground">
        MindOS &bull; Attention &amp; Time Operating System &bull; Controlled Chaos &bull; sys.0.1
      </footer>
    </div>
  )
}

export default App
