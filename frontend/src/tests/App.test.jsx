import { render, screen } from '@testing-library/react'
import { beforeEach, describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import App from '@/App'

const BASE = 'http://goatfarm.local/api/v1'

describe('App shell', () => {
  // BrowserRouter reads window.location; reset it so tests don't leak routes.
  beforeEach(() => window.history.pushState({}, '', '/'))

  it('redirects to login when not authenticated', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('boots the admin shell and lands on the dashboard when authenticated', async () => {
    localStorage.setItem('access_token', 'test-token')
    // Dashboard fires these on mount — mock them so MSW stays in strict mode.
    server.use(
      http.get(`${BASE}/goats/`, () => HttpResponse.json({ count: 0, results: [] })),
      http.get(`${BASE}/alerts/`, () =>
        HttpResponse.json({ overdue: [], due_soon: [] }),
      ),
      http.get(`${BASE}/health/`, () => HttpResponse.json({ count: 0, results: [] })),
    )
    render(<App />)
    // Sidebar logo sub-label is unique to the shell.
    expect(await screen.findByText('Farm OS v1.0')).toBeInTheDocument()
  })
})

// The worker /g/:uuid route is covered by src/pages/worker/GoatProfile.test.jsx.
