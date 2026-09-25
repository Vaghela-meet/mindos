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
    <Card className="border-border bg-card">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="flex items-center space-x-2">
            <Server className="h-4 w-4 text-accent" />
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

      <CardContent className="space-y-4 pt-2">
        {loading && (
          <div className="flex items-center space-x-2 text-muted-foreground">
            <RefreshCw className="h-4 w-4 animate-spin text-accent" />
            <span>Checking endpoint `/api/v1/health`...</span>
          </div>
        )}

        {error && !loading && (
          <div className="rounded-sm border border-status-attention/30 bg-status-attention/10 p-3 text-status-attention">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-status-attention flex-shrink-0" />
              <div>
                <p className="font-semibold text-xs">Backend Service Offline or Unreachable</p>
                <p className="text-[11px] text-foreground/80 mt-0.5">
                  Start the backend with <code className="bg-secondary px-1 py-0.5 rounded-sm font-mono text-[11px] text-foreground">uvicorn app.main:app --port 8000</code> to view live telemetry.
                </p>
              </div>
            </div>
          </div>
        )}

        {data && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="rounded-sm border border-border bg-secondary/30 p-3 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">FastAPI Core</span>
                <Badge variant="healthy" className="flex items-center space-x-1 text-[10px]">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{data.status.toUpperCase()}</span>
                </Badge>
              </div>
              <div className="text-xs text-foreground/80 space-y-0.5">
                <div>Application: <span className="font-medium text-foreground">{data.app}</span></div>
                <div>Version: <span className="font-mono text-foreground">{data.version}</span></div>
                <div>Environment: <span className="font-medium text-foreground">{data.environment}</span></div>
              </div>
            </div>

            <div className="rounded-sm border border-border bg-secondary/30 p-3 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider flex items-center space-x-1">
                  <Database className="h-3 w-3 text-accent" />
                  <span>Database Layer</span>
                </span>
                <Badge
                  variant={data.database.status === 'connected' ? 'healthy' : 'attention'}
                  className="text-[10px]"
                >
                  {data.database.status.toUpperCase()}
                </Badge>
              </div>
              <div className="text-xs text-foreground/80 space-y-0.5">
                <div>Engine: <span className="font-medium text-foreground capitalize">{data.database.database}</span></div>
                {data.database.detail && (
                  <div className="text-xs text-status-attention">{data.database.detail}</div>
                )}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
