import { describe, expect, it } from 'vitest'
import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { renderAtRoute } from '@/tests/utils'
import Dashboard from '@/pages/admin/Dashboard'

const GOATS_URL = 'http://goatfarm.local/api/v1/goats/'
const ALERTS_URL = 'http://goatfarm.local/api/v1/alerts/'
const HEALTH_URL = 'http://goatfarm.local/api/v1/health/'

const goats = [
  {
    id: 'g1',
    tag_number: 'G-1',
    name: 'Daisy',
    sex_display: 'Female',
    current_area: 'a1',
    current_area_name: 'Pen A',
    status: 'active',
    status_display: 'Active',
  },
]
const overdueRecord = {
  id: 'h1',
  goat: 'g1',
  goat_tag_number: 'G-1',
  record_type_display: 'Vaccination',
  record_date: '2026-01-01',
  next_due_date: '2026-05-01',
  status: 'overdue',
}

function mockAll({ overdue = [overdueRecord] } = {}) {
  server.use(
    http.get(GOATS_URL, () => HttpResponse.json({ count: 1, results: goats })),
    http.get(ALERTS_URL, () => HttpResponse.json({ overdue, due_soon: [] })),
    http.get(HEALTH_URL, () =>
      HttpResponse.json({ count: 1, results: [overdueRecord] }),
    ),
  )
}

function renderDashboard() {
  return renderAtRoute(<Dashboard />, { path: '/dashboard', entry: '/dashboard' })
}

describe('Dashboard', () => {
  it('renders stat cards', async () => {
    mockAll()
    renderDashboard()
    expect(await screen.findByText(/total goats/i)).toBeInTheDocument()
    expect(screen.getByText(/overdue/i)).toBeInTheDocument()
    expect(screen.getByText(/due this week/i)).toBeInTheDocument()
    expect(screen.getByText(/active pens/i)).toBeInTheDocument()
  })

  it('shows overdue alerts in red', async () => {
    mockAll()
    const { container } = renderDashboard()
    await screen.findByText(/total goats/i)
    // the overdue alert row carries an alert-toned element
    expect(container.querySelector('.border-alert, .text-alert')).toBeTruthy()
  })

  it('renders correctly on a mobile viewport (375px)', async () => {
    window.innerWidth = 375
    mockAll()
    renderDashboard()
    const statRow = await screen.findByTestId('stat-cards')
    expect(statRow.className).toMatch(/sm:grid-cols-2/)
  })
})
