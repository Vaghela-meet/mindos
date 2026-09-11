import React, { useState } from 'react'
import { Availability, DayOfWeek } from '@/types/domain'
import { Clock, Plus, Trash2, Edit2, Check, X, AlertCircle, Calendar } from 'lucide-react'

interface AvailabilityViewProps {
  availabilities: Availability[]
  onCreate: (payload: { day_of_week: DayOfWeek; start_time: string; end_time: string }) => Promise<void>
  onUpdate: (id: number, payload: Partial<{ day_of_week: DayOfWeek; start_time: string; end_time: string }>) => Promise<void>
  onDelete: (id: number) => Promise<void>
  loading?: boolean
}

const DAYS_OF_WEEK: { key: DayOfWeek; label: string; short: string }[] = [
  { key: 'MONDAY', label: 'Monday', short: 'Mon' },
  { key: 'TUESDAY', label: 'Tuesday', short: 'Tue' },
  { key: 'WEDNESDAY', label: 'Wednesday', short: 'Wed' },
  { key: 'THURSDAY', label: 'Thursday', short: 'Thu' },
  { key: 'FRIDAY', label: 'Friday', short: 'Fri' },
  { key: 'SATURDAY', label: 'Saturday', short: 'Sat' },
  { key: 'SUNDAY', label: 'Sunday', short: 'Sun' },
]

function formatTimeDisplay(timeStr: string): string {
  // Format "09:00:00" -> "09:00"
  if (!timeStr) return ''
  const parts = timeStr.split(':')
  return `${parts[0]}:${parts[1]}`
}

function calculateDurationMinutes(start: string, end: string): number {
  if (!start || !end) return 0
  const [h1, m1] = start.split(':').map(Number)
  const [h2, m2] = end.split(':').map(Number)
  return (h2 * 60 + m2) - (h1 * 60 + m1)
}

function formatDuration(minutes: number): string {
  if (minutes <= 0) return '0m'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0 && m > 0) return `${h}h ${m}m`
  if (h > 0) return `${h}h`
  return `${m}m`
}

export const AvailabilityView: React.FC<AvailabilityViewProps> = ({
  availabilities,
  onCreate,
  onUpdate,
  onDelete,
  loading = false,
}) => {
  const [selectedDay, setSelectedDay] = useState<DayOfWeek>('MONDAY')
  const [startTime, setStartTime] = useState<string>('09:00')
  const [endTime, setEndTime] = useState<string>('17:00')
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Edit state
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editStart, setEditStart] = useState<string>('')
  const [editEnd, setEditEnd] = useState<string>('')
  const [editError, setEditError] = useState<string | null>(null)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setSubmitting(true)
    try {
      await onCreate({
        day_of_week: selectedDay,
        start_time: startTime.length === 5 ? `${startTime}:00` : startTime,
        end_time: endTime.length === 5 ? `${endTime}:00` : endTime,
      })
      // Reset form defaults
      setStartTime('09:00')
      setEndTime('17:00')
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create availability window')
    } finally {
      setSubmitting(false)
    }
  }

  const startEdit = (window: Availability) => {
    setEditingId(window.id)
    setEditStart(formatTimeDisplay(window.start_time))
    setEditEnd(formatTimeDisplay(window.end_time))
    setEditError(null)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditStart('')
    setEditEnd('')
    setEditError(null)
  }

  const saveEdit = async (window: Availability) => {
    setEditError(null)
    try {
      await onUpdate(window.id, {
        start_time: editStart.length === 5 ? `${editStart}:00` : editStart,
        end_time: editEnd.length === 5 ? `${editEnd}:00` : editEnd,
      })
      setEditingId(null)
    } catch (err: any) {
      setEditError(err.message || 'Failed to update window')
    }
  }

  // Calculate total weekly hours
  const totalWeeklyMinutes = availabilities.reduce((acc, curr) => {
    return acc + calculateDurationMinutes(curr.start_time, curr.end_time)
  }, 0)

  return (
    <div className="space-y-6">
      {/* Top Overview & Summary */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-sm font-medium text-slate-200">
            <Clock className="h-4 w-4 text-emerald-400" />
            <span>Weekly Work Capacity</span>
          </div>
          <p className="text-xs text-slate-400">
            Define recurring working hours. These windows represent your baseline capacity for scheduling.
          </p>
        </div>

        <div className="flex items-center space-x-3 bg-slate-950/80 border border-slate-800 rounded-lg px-4 py-2">
          <div className="text-right">
            <div className="text-xs text-slate-400">Total Capacity</div>
            <div className="text-lg font-bold text-emerald-400">
              {formatDuration(totalWeeklyMinutes)} / week
            </div>
          </div>
        </div>
      </div>

      {/* Add New Availability Window Section */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-3">
          <Plus className="h-4 w-4 text-blue-400" />
          Add Availability Window
        </h3>

        {errorMessage && (
          <div className="mb-4 flex items-center gap-2 p-3 rounded-lg border border-red-500/30 bg-red-950/40 text-xs text-red-300">
            <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleCreate} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Weekday</label>
            <select
              value={selectedDay}
              onChange={(e) => setSelectedDay(e.target.value as DayOfWeek)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-blue-500 focus:outline-none"
            >
              {DAYS_OF_WEEK.map((d) => (
                <option key={d.key} value={d.key}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Start Time</label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">End Time</label>
            <input
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-blue-600 px-4 py-2 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-1.5 shadow-sm"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>{submitting ? 'Adding...' : 'Add Window'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Weekday Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {DAYS_OF_WEEK.map((day) => {
          const dayWindows = availabilities.filter((a) => a.day_of_week === day.key)
          const dayMinutes = dayWindows.reduce((acc, curr) => {
            return acc + calculateDurationMinutes(curr.start_time, curr.end_time)
          }, 0)

          return (
            <div
              key={day.key}
              className={`rounded-xl border flex flex-col justify-between transition-colors ${
                dayWindows.length > 0
                  ? 'border-slate-800 bg-slate-900/50'
                  : 'border-slate-800/60 bg-slate-950/40'
              } p-4`}
            >
              <div>
                {/* Day Header */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-3">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-3.5 w-3.5 text-blue-400" />
                    <span className="text-sm font-semibold text-white">{day.label}</span>
                  </div>
                  <span
                    className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
                      dayMinutes > 0
                        ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                        : 'text-slate-500'
                    }`}
                  >
                    {formatDuration(dayMinutes)}
                  </span>
                </div>

                {/* Windows list */}
                {loading ? (
                  <div className="py-4 text-center text-xs text-slate-500">Loading...</div>
                ) : dayWindows.length === 0 ? (
                  <div className="py-6 text-center text-xs text-slate-500 italic">
                    No availability set
                  </div>
                ) : (
                  <div className="space-y-2">
                    {dayWindows.map((window) => {
                      const isEditing = editingId === window.id
                      const duration = calculateDurationMinutes(window.start_time, window.end_time)

                      return (
                        <div
                          key={window.id}
                          className="rounded-lg border border-slate-800 bg-slate-950 p-2.5 text-xs text-slate-200 transition-all hover:border-slate-700"
                        >
                          {isEditing ? (
                            <div className="space-y-2">
                              {editError && (
                                <div className="text-[10px] text-red-400 leading-tight">
                                  {editError}
                                </div>
                              )}
                              <div className="flex items-center gap-1.5">
                                <input
                                  type="time"
                                  value={editStart}
                                  onChange={(e) => setEditStart(e.target.value)}
                                  className="w-full rounded border border-slate-700 bg-slate-900 px-1.5 py-1 text-xs text-white"
                                />
                                <span className="text-slate-500">&ndash;</span>
                                <input
                                  type="time"
                                  value={editEnd}
                                  onChange={(e) => setEditEnd(e.target.value)}
                                  className="w-full rounded border border-slate-700 bg-slate-900 px-1.5 py-1 text-xs text-white"
                                />
                              </div>
                              <div className="flex justify-end gap-1 pt-1">
                                <button
                                  onClick={() => saveEdit(window)}
                                  className="rounded bg-emerald-600 p-1 text-white hover:bg-emerald-500"
                                  title="Save"
                                >
                                  <Check className="h-3.5 w-3.5" />
                                </button>
                                <button
                                  onClick={cancelEdit}
                                  className="rounded bg-slate-700 p-1 text-slate-300 hover:bg-slate-600"
                                  title="Cancel"
                                >
                                  <X className="h-3.5 w-3.5" />
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <span className="font-mono text-xs text-slate-200">
                                  {formatTimeDisplay(window.start_time)} &ndash; {formatTimeDisplay(window.end_time)}
                                </span>
                                <span className="text-[10px] text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">
                                  {formatDuration(duration)}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => startEdit(window)}
                                  className="text-slate-400 hover:text-blue-400 p-1 rounded hover:bg-slate-800 transition-colors"
                                  title="Edit Window"
                                >
                                  <Edit2 className="h-3 w-3" />
                                </button>
                                <button
                                  onClick={() => onDelete(window.id)}
                                  className="text-slate-400 hover:text-red-400 p-1 rounded hover:bg-slate-800 transition-colors"
                                  title="Delete Window"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>

              {/* Quick Add For This Day */}
              <div className="pt-3 mt-3 border-t border-slate-800/60 flex justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedDay(day.key)
                    window.scrollTo({ top: 180, behavior: 'smooth' })
                  }}
                  className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
                >
                  <Plus className="h-3 w-3" />
                  <span>Add for {day.short}</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
