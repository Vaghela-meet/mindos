import React from 'react'
import { Activity, Brain, Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white">MindOS</span>
              <Badge variant="default">v0.1.0-alpha</Badge>
            </div>
            <p className="text-xs text-slate-400">Adaptive Personal Productivity Operating System</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Activity className="h-4 w-4 text-emerald-400" />
            <span>Modular Monolith Foundation</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-blue-400 bg-blue-950/50 border border-blue-800/50 px-3 py-1.5 rounded-md">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Target: PostgreSQL</span>
          </div>
        </div>
      </div>
    </header>
  )
}
