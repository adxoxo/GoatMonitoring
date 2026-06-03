import { describe, expect, it } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { renderAtRoute } from '@/tests/utils'
import HealthRecords from '@/pages/admin/HealthRecords'

const HEALTH_URL = 'http://goatfarm.local/api/v1/health/'
const ALERTS_URL = 'http://goatfarm.local/api/v1/alerts/'

const records = [
  {
    id: 'h1',
    goat: 'g1',
    goat_tag_number: 'G-001',
    record_type: 'vaccination',
    record_type_display: 'Vaccination',
    record_date: '2026-01-10',
    next_due_date: '2027-01-10',
    status: 'on_schedule',
  },
  {
    id: 'h2',
    goat: 'g2',
    goat_tag_number: 'G-002',
    record_type: 'checkup',
    record_type_display: 'Checkup',
    record_date: '2026-02-01',
    next_due_date: null,
    status: 'none',
  },
]

function mockHealth(rows = records) {
  server.use(
    http.get(HEALTH_URL, ({ request }) => {
      const type = new URL(request.url).searchParams.get('record_type')
      const filtered = type ? rows.filter((r) => r.record_type === type) : rows
      return HttpResponse.json({ count: filtered.length, results: filtered })
    }),
    http.get(ALERTS_URL, () => HttpResponse.json({ overdue: [], due_soon: [] })),
  )
}

function renderPage() {
  return renderAtRoute(<HealthRecords />, { path: '/health', entry: '/health' })
}

describe('HealthRecords page', () => {
  it('renders the records table', async () => {
    mockHealth()
    renderPage()
    expect(await screen.findByText('G-001')).toBeInTheDocument()
    expect(screen.getByText('G-002')).toBeInTheDocument()
    // record_date cell is unique to the table (tab labels collide with type names)
    expect(screen.getByText('2026-01-10')).toBeInTheDocument()
  })

  it('tab filter changes displayed records', async () => {
    mockHealth()
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('G-002') // checkup row present initially
    await user.click(screen.getByRole('button', { name: /vaccination/i }))
    expect(await screen.findByText('G-001')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.queryByText('G-002')).not.toBeInTheDocument(),
    )
  })

  it('shows an empty state when there are no records', async () => {
    mockHealth([])
    renderPage()
    expect(await screen.findByText(/no records/i)).toBeInTheDocument()
  })
})
