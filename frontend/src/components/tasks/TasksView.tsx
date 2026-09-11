import React, { useState } from 'react'
import { CheckSquare, Square, Plus, Clock, CheckCircle2, ListTodo } from 'lucide-react'
import { Goal, Task, TaskPriority } from '@/types/domain'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface TasksViewProps {
  selectedGoal: Goal | null
  tasks: Task[]
  onCreateTask: (payload: {
    goal_id: number
    title: string
    description?: string
    priority?: TaskPriority
    estimated_minutes?: number
  }) => Promise<void>
  onToggleComplete: (task: Task) => Promise<void>
  loading?: boolean
}

export const TasksView: React.FC<TasksViewProps> = ({
  selectedGoal,
  tasks,
  onCreateTask,
  onToggleComplete,
  loading = false,
}) => {
  const [isCreating, setIsCreating] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<TaskPriority>('MEDIUM')
  const [estimatedMinutes, setEstimatedMinutes] = useState<string>('30')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!selectedGoal) {
    return (
      <Card className="border-slate-800 bg-slate-900/60 h-full flex flex-col justify-center items-center py-16 text-center text-slate-500">
        <ListTodo className="h-10 w-10 text-slate-600 mb-3" />
        <h3 className="text-base font-medium text-slate-300">No Goal Selected</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-xs">
          Select a Goal from the list to view, create, and manage its execution tasks.
        </p>
      </Card>
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !selectedGoal) return

    const parsedMinutes = estimatedMinutes ? parseInt(estimatedMinutes, 10) : undefined
    if (parsedMinutes !== undefined && (isNaN(parsedMinutes) || parsedMinutes <= 0)) {
      setError('Estimated minutes must be a positive number (> 0)')
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      await onCreateTask({
        goal_id: selectedGoal.id,
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        estimated_minutes: parsedMinutes,
      })
      setTitle('')
      setDescription('')
      setEstimatedMinutes('30')
      setPriority('MEDIUM')
      setIsCreating(false)
    } catch (err: any) {
      setError(err.message || 'Failed to create task')
    } finally {
      setSubmitting(false)
    }
  }

  const priorityBadge = (p: TaskPriority) => {
    switch (p) {
      case 'HIGH':
        return <Badge variant="warning">HIGH</Badge>
      case 'MEDIUM':
        return <Badge variant="default">MEDIUM</Badge>
      case 'LOW':
        return <Badge variant="secondary">LOW</Badge>
    }
  }

  return (
    <Card className="border-slate-800 bg-slate-900/60">
      <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-slate-800/60">
        <div>
          <div className="flex items-center space-x-2">
            <CheckSquare className="h-5 w-5 text-emerald-400" />
            <CardTitle className="text-base font-bold text-white">
              Tasks &bull; <span className="text-slate-400 font-normal">{selectedGoal.title}</span>
            </CardTitle>
            <Badge variant="outline">{tasks.length}</Badge>
          </div>
        </div>
        {!isCreating && (
          <Button
            size="sm"
            onClick={() => setIsCreating(true)}
            className="flex items-center space-x-1"
          >
            <Plus className="h-4 w-4" />
            <span>New Task</span>
          </Button>
        )}
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {isCreating && (
          <form onSubmit={handleSubmit} className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 space-y-3">
            <h4 className="text-sm font-semibold text-white">Add Task to {selectedGoal.title}</h4>
            {error && <p className="text-xs text-rose-400">{error}</p>}
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Task Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Draft initial specifications"
                required
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Task details and deliverables..."
                rows={2}
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Estimated Minutes</label>
                <input
                  type="number"
                  min="1"
                  value={estimatedMinutes}
                  onChange={(e) => setEstimatedMinutes(e.target.value)}
                  placeholder="30"
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as TaskPriority)}
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setIsCreating(false)}
                disabled={submitting}
              >
                Cancel
              </Button>
              <Button type="submit" size="sm" disabled={submitting || !title.trim()}>
                {submitting ? 'Adding...' : 'Add Task'}
              </Button>
            </div>
          </form>
        )}

        {loading && tasks.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-6">Loading tasks...</p>
        )}

        {!loading && tasks.length === 0 && !isCreating && (
          <div className="text-center py-8 text-slate-500 space-y-1">
            <p className="text-sm text-slate-400">No tasks in this goal.</p>
            <p className="text-xs">Add execution tasks to break down this goal.</p>
          </div>
        )}

        <div className="space-y-2">
          {tasks.map((task) => {
            const isCompleted = task.status === 'COMPLETED'
            return (
              <div
                key={task.id}
                className={`flex items-start justify-between rounded-lg border p-3.5 transition-all ${
                  isCompleted
                    ? 'border-emerald-900/40 bg-emerald-950/20 text-slate-400'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <button
                    type="button"
                    onClick={() => onToggleComplete(task)}
                    className="mt-0.5 text-slate-400 hover:text-emerald-400 transition-colors focus:outline-none"
                    aria-label={isCompleted ? 'Mark task incomplete' : 'Mark task completed'}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                    ) : (
                      <Square className="h-5 w-5 text-slate-500 hover:text-white" />
                    )}
                  </button>
                  <div className="space-y-1">
                    <span
                      className={`text-sm font-medium ${
                        isCompleted ? 'line-through text-slate-400' : 'text-white'
                      }`}
                    >
                      {task.title}
                    </span>
                    {task.description && (
                      <p className="text-xs text-slate-400 line-clamp-2">{task.description}</p>
                    )}
                    <div className="flex items-center space-x-3 text-[11px] text-slate-400 pt-1">
                      {task.estimated_minutes && (
                        <span className="flex items-center space-x-1">
                          <Clock className="h-3 w-3 text-blue-400" />
                          <span>{task.estimated_minutes}m</span>
                        </span>
                      )}
                      {task.completed_at && (
                        <span className="text-emerald-400/90">
                          Completed {new Date(task.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  {priorityBadge(task.priority)}
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
