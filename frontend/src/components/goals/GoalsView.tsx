import React, { useState } from 'react'
import { Plus, Target, CheckCircle2, AlertCircle } from 'lucide-react'
import { Goal, GoalPriority } from '@/types/domain'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface GoalsViewProps {
  goals: Goal[]
  selectedGoalId: number | null
  onSelectGoal: (goalId: number) => void
  onCreateGoal: (payload: { title: string; description?: string; priority: GoalPriority }) => Promise<void>
  loading?: boolean
}

export const GoalsView: React.FC<GoalsViewProps> = ({
  goals,
  selectedGoalId,
  onSelectGoal,
  onCreateGoal,
  loading = false,
}) => {
  const [isCreating, setIsCreating] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<GoalPriority>('MEDIUM')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setSubmitting(true)
    setError(null)
    try {
      await onCreateGoal({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
      })
      setTitle('')
      setDescription('')
      setPriority('MEDIUM')
      setIsCreating(false)
    } catch (err: any) {
      setError(err.message || 'Failed to create goal')
    } finally {
      setSubmitting(false)
    }
  }

  const priorityBadge = (p: GoalPriority) => {
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
        <div className="flex items-center space-x-2">
          <Target className="h-5 w-5 text-sky-400" />
          <CardTitle className="text-base font-bold text-white">Goals</CardTitle>
          <Badge variant="outline">{goals.length}</Badge>
        </div>
        {!isCreating && (
          <Button
            size="sm"
            onClick={() => setIsCreating(true)}
            className="flex items-center space-x-1"
          >
            <Plus className="h-4 w-4" />
            <span>New Goal</span>
          </Button>
        )}
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {isCreating && (
          <form onSubmit={handleSubmit} className="rounded-lg border border-slate-800 bg-slate-950/70 p-4 space-y-3">
            <h4 className="text-sm font-semibold text-white">Create New Goal</h4>
            {error && <p className="text-xs text-rose-400">{error}</p>}
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Goal Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Master Time Management"
                required
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Why this goal matters..."
                rows={2}
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <label className="block text-xs font-medium text-slate-400 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as GoalPriority)}
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
                {submitting ? 'Creating...' : 'Create Goal'}
              </Button>
            </div>
          </form>
        )}

        {loading && goals.length === 0 && (
          <p className="text-xs text-slate-400 text-center py-6">Loading goals...</p>
        )}

        {!loading && goals.length === 0 && !isCreating && (
          <div className="text-center py-8 text-slate-500 space-y-2">
            <AlertCircle className="h-8 w-8 mx-auto text-slate-600" />
            <p className="text-sm">No goals created yet.</p>
            <p className="text-xs">Create your first goal to begin adding tasks.</p>
          </div>
        )}

        <div className="space-y-2">
          {goals.map((goal) => {
            const isSelected = goal.id === selectedGoalId
            return (
              <div
                key={goal.id}
                onClick={() => onSelectGoal(goal.id)}
                className={`cursor-pointer rounded-lg border p-3.5 transition-all text-left ${
                  isSelected
                    ? 'border-blue-500/80 bg-blue-950/30 shadow-md ring-1 ring-blue-500/30'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-sm text-white">{goal.title}</span>
                      {goal.status === 'COMPLETED' && (
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                      )}
                    </div>
                    {goal.description && (
                      <p className="text-xs text-slate-400 line-clamp-2">{goal.description}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    {priorityBadge(goal.priority)}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
