import React, { useEffect, useState } from 'react'
import { Header } from '@/components/Header'
import { HealthCheck } from '@/components/HealthCheck'
import { GoalsView } from '@/components/goals/GoalsView'
import { TasksView } from '@/components/tasks/TasksView'
import { AvailabilityView } from '@/components/availability/AvailabilityView'
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
import { Sparkles, Target, CalendarDays } from 'lucide-react'

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'goals' | 'availability'>('goals')

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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Milestone Banner */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 p-6 shadow-2xl">
          <div className="relative z-10 max-w-3xl space-y-2">
            <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
              <Sparkles className="h-3.5 w-3.5 text-blue-400" />
              <span>MindOS Domain Engine &bull; M1 Goals &bull; M2 Availability</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              {activeTab === 'goals' ? 'Goals & Tasks Management' : 'Weekly Availability Capacity'}
            </h1>
            <p className="text-xs text-slate-300 leading-relaxed">
              {activeTab === 'goals'
                ? 'Execution primitives for MindOS. Tasks belong strictly to high-level Goals with conservative deletion protecting your progress.'
                : 'Configurable weekly working capacity. Represents when you are generally available to execute planned tasks.'}
            </p>
          </div>
        </div>

        {/* Backend Health Check */}
        <section>
          <HealthCheck />
        </section>

        {/* Domain Navigation Tabs */}
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
          <button
            onClick={() => setActiveTab('goals')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'goals'
                ? 'bg-blue-600/20 border border-blue-500/40 text-blue-300 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Target className="h-4 w-4 text-blue-400" />
            <span>Goals &bull; Tasks</span>
            <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded-full text-slate-300">
              {goals.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('availability')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'availability'
                ? 'bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <CalendarDays className="h-4 w-4 text-emerald-400" />
            <span>Weekly Availability</span>
            <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded-full text-slate-300">
              {availabilities.length}
            </span>
          </button>
        </div>

        {/* Tab Views */}
        {activeTab === 'goals' ? (
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
        ) : (
          <section>
            <AvailabilityView
              availabilities={availabilities}
              onCreate={handleCreateAvailability}
              onUpdate={handleUpdateAvailability}
              onDelete={handleDeleteAvailability}
              loading={loadingAvailabilities}
            />
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        MindOS &bull; Modular Monolith &bull; React + TypeScript + FastAPI + PostgreSQL Target
      </footer>
    </div>
  )
}

export default App
