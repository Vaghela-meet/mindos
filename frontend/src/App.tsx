import React from 'react'
import {
  Calendar,
  CheckSquare,
  Compass,
  Cpu,
  Mic,
  Sliders,
  Timer,
  Layers,
  Sparkles,
} from 'lucide-react'
import { Header } from '@/components/Header'
import { HealthCheck } from '@/components/HealthCheck'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

export const App: React.FC = () => {
  const serviceModules = [
    {
      name: 'Task Service',
      domain: 'backend/app/services/task',
      description: 'Granular units of execution, deadlines, durations, and priorities.',
      icon: CheckSquare,
      color: 'text-emerald-400',
    },
    {
      name: 'Goal Service',
      domain: 'backend/app/services/goal',
      description: 'Long-term intent, progressive milestones, and target outcomes.',
      icon: Compass,
      color: 'text-sky-400',
    },
    {
      name: 'Planning Service',
      domain: 'backend/app/services/planning',
      description: 'Intelligent daily schedules matching user availability and attention.',
      icon: Calendar,
      color: 'text-indigo-400',
    },
    {
      name: 'Adaptation Service',
      domain: 'backend/app/services/adaptation',
      description: 'Dynamic rescheduling and real-time friction recovery when routines break.',
      icon: Sliders,
      color: 'text-amber-400',
    },
    {
      name: 'Focus Service',
      domain: 'backend/app/services/focus',
      description: 'Focused execution sessions, deep work timers, and attention shields.',
      icon: Timer,
      color: 'text-rose-400',
    },
    {
      name: 'AI Service',
      domain: 'backend/app/services/ai',
      description: 'Provider-agnostic intelligence for synthesis, planning, and suggestions.',
      icon: Cpu,
      color: 'text-purple-400',
    },
    {
      name: 'Voice Service',
      domain: 'backend/app/services/voice',
      description: 'Natural speech capture and low-friction command processing.',
      icon: Mic,
      color: 'text-teal-400',
    },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Welcome Hero */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 p-8 shadow-2xl">
          <div className="relative z-10 max-w-2xl space-y-3">
            <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
              <Sparkles className="h-3.5 w-3.5 text-blue-400" />
              <span>Foundation Phase Bootstrapped</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              MindOS Operating System
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              MindOS manages available attention over time rather than static lists.
              The foundation layer is configured with a modular monolith architecture,
              connecting React + TypeScript to a FastAPI backend targeting PostgreSQL.
            </p>
          </div>
        </div>

        {/* Backend Health Check */}
        <section>
          <HealthCheck />
        </section>

        {/* Modular Monolith Architecture Domains */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Layers className="h-5 w-5 text-blue-400" />
              <h2 className="text-xl font-bold tracking-tight text-white">
                Application Domain Services
              </h2>
            </div>
            <Badge variant="secondary">7 Domains Scaffolding Ready</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {serviceModules.map((service) => {
              const Icon = service.icon
              return (
                <Card
                  key={service.name}
                  className="transition-all hover:border-slate-700 hover:shadow-lg bg-slate-900/50"
                >
                  <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/60">
                        <Icon className={`h-5 w-5 ${service.color}`} />
                      </div>
                      <CardTitle className="text-base">{service.name}</CardTitle>
                    </div>
                    <Badge variant="outline">Scaffolded</Badge>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-2">
                    <CardDescription className="text-xs leading-relaxed">
                      {service.description}
                    </CardDescription>
                    <div className="text-[11px] font-mono text-slate-400 bg-slate-950/80 p-1.5 rounded border border-slate-800">
                      {service.domain}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-400">
        MindOS Foundation Scaffold &bull; Modular Monolith Architecture &bull; React + FastAPI + PostgreSQL
      </footer>
    </div>
  )
}

export default App
