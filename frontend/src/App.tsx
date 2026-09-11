import React, { useEffect, useState } from 'react'
import { Header } from '@/components/Header'
import { HealthCheck } from '@/components/HealthCheck'
import { GoalsView } from '@/components/goals/GoalsView'
import { TasksView } from '@/components/tasks/TasksView'
import { Goal, Task, GoalPriority, TaskPriority } from '@/types/domain'
import { getGoals, createGoal, getTasks, createTask, updateTask } from '@/api/client'
import { Sparkles } from 'lucide-react'

export const App: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([])
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loadingGoals, setLoadingGoals] = useState<boolean>(false)
  const [loadingTasks, setLoadingTasks] = useState<boolean>(false)

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

  useEffect(() => {
    loadGoals()
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

  const selectedGoal = goals.find((g) => g.id === selectedGoalId) || null

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* M1 Banner */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 p-6 shadow-2xl">
          <div className="relative z-10 max-w-3xl space-y-2">
            <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
              <Sparkles className="h-3.5 w-3.5 text-blue-400" />
              <span>M1 &bull; Goals + Tasks Domain</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Goals &bull; Tasks Management
            </h1>
            <p className="text-xs text-slate-300 leading-relaxed">
              Execution primitives for MindOS. Tasks belong strictly to high-level Goals.
              Conservative deletion prevents cascading data loss, ensuring your work and history remain safe.
            </p>
          </div>
        </div>

        {/* Backend Health Check */}
        <section>
          <HealthCheck />
        </section>

        {/* Goals & Tasks Interactive Domain Workspace */}
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
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        MindOS &bull; Modular Monolith &bull; React + TypeScript + FastAPI + PostgreSQL Target
      </footer>
    </div>
  )
}

export default App
