import React, { useEffect, useState } from 'react'
import { CheckCircle2, AlertTriangle, RefreshCw, Server, Database } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'

interface HealthData {
  status: string
  app: string
  version: string
  environment: string
  database: {
    status: string
    database: string
    detail?: string
  }
}

export const HealthCheck: React.FC = () => {
  const [data, setData] = useState<HealthData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
      const response = await fetch(`${baseUrl}/health`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const json = await response.json()
      setData(json)
    } catch (err: any) {
      setError(err.message || 'Unable to connect to backend service')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

  return (
    <Card className="border-slate-800 bg-slate-900/70">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="flex items-center space-x-2">
            <Server className="h-5 w-5 text-blue-400" />
            <span>Backend Integration Status</span>
          </CardTitle>
          <CardDescription>
            Live status of the FastAPI backend and PostgreSQL data layer
          </CardDescription>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={fetchHealth}
          disabled={loading}
          className="flex items-center space-x-1.5"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Check Health</span>
        </Button>
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        {loading && (
          <div className="flex items-center space-x-2 text-slate-400">
            <RefreshCw className="h-4 w-4 animate-spin text-blue-400" />
            <span>Checking endpoint `/api/v1/health`...</span>
          </div>
        )}

        {error && !loading && (
          <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-4 text-amber-300">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0" />
              <div>
                <p className="font-semibold text-sm">Backend Service Offline or Unreachable</p>
                <p className="text-xs text-amber-200/80 mt-1">
                  Start the backend with <code className="bg-amber-950/60 px-1 py-0.5 rounded text-white">uvicorn app.main:app --port 8000</code> to view live telemetry.
                </p>
              </div>
            </div>
          </div>
        )}

        {data && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 uppercase tracking-wider">FastAPI Core</span>
                <Badge variant="success" className="flex items-center space-x-1">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{data.status.toUpperCase()}</span>
                </Badge>
              </div>
              <div className="text-xs text-slate-300 space-y-1">
                <div>Application: <span className="font-medium text-white">{data.app}</span></div>
                <div>Version: <span className="font-mono text-white">{data.version}</span></div>
                <div>Environment: <span className="font-medium text-white">{data.environment}</span></div>
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 uppercase tracking-wider flex items-center space-x-1">
                  <Database className="h-3.5 w-3.5 text-blue-400" />
                  <span>Database Layer</span>
                </span>
                <Badge
                  variant={data.database.status === 'connected' ? 'success' : 'warning'}
                >
                  {data.database.status.toUpperCase()}
                </Badge>
              </div>
              <div className="text-xs text-slate-300 space-y-1">
                <div>Engine: <span className="font-medium text-white capitalize">{data.database.database}</span></div>
                {data.database.detail && (
                  <div className="text-xs text-amber-400/90">{data.database.detail}</div>
                )}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
