import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'

// Mock fetch for healthcheck in test environment
global.fetch = vi.fn().mockImplementation(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        status: 'ok',
        app: 'MindOS',
        version: '0.1.0',
        environment: 'development',
        database: {
          status: 'connected',
          database: 'postgresql',
        },
      }),
  })
)

describe('MindOS App Shell', () => {
  it('renders application brand and main heading', async () => {
    render(<App />)
    expect(screen.getByText('MindOS Operating System')).toBeInTheDocument()
    expect(screen.getByText('Task Service')).toBeInTheDocument()
    expect(screen.getByText('Planning Service')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Backend Integration Status')).toBeInTheDocument()
    })
  })

  it('renders all modular monolith domain services', async () => {
    render(<App />)
    expect(screen.getByText('Goal Service')).toBeInTheDocument()
    expect(screen.getByText('Adaptation Service')).toBeInTheDocument()
    expect(screen.getByText('Focus Service')).toBeInTheDocument()
    expect(screen.getByText('AI Service')).toBeInTheDocument()
    expect(screen.getByText('Voice Service')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('FastAPI Core')).toBeInTheDocument()
    })
  })
})
