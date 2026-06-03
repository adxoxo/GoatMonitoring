import { describe, expect, it } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { renderAtRoute } from '@/tests/utils'
import GoatList from '@/pages/admin/GoatList'

const GOATS_URL = 'http://goatfarm.local/api/v1/goats/'

const goats = [
  {
    id: 'g1',
    tag_number: 'G-001',
    name: 'Daisy',
    sex_display: 'Female',
    current_area_name: 'Pen A',
    status: 'active',
    status_display: 'Active',
  },
  {
    id: 'g2',
    tag_number: 'G-002',
    name: 'Bolt',
    sex_display: 'Male',
    current_area_name: 'Pen B',
    status: 'sold',
    status_display: 'Sold',
  },
]

function mockGoats(rows = goats) {
  server.use(
    http.get(GOATS_URL, ({ request }) => {
      const url = new URL(request.url)
      const search = url.searchParams.get('search')
      const status = url.searchParams.get('status')
      let out = rows
      if (search) {
        const q = search.toLowerCase()
        out = out.filter(
          (g) =>
            g.tag_number.toLowerCase().includes(q) ||
            (g.name || '').toLowerCase().includes(q),
        )
      }
      if (status) out = out.filter((g) => g.status === status)
      return HttpResponse.json({ count: out.length, results: out })
    }),
  )
}

function renderList() {
  return renderAtRoute(<GoatList />, { path: '/goats', entry: '/goats' })
}

describe('GoatList page', () => {
  it('renders a row for each goat', async () => {
    mockGoats()
    renderList()
    expect(await screen.findByText('G-001')).toBeInTheDocument()
    expect(screen.getByText('G-002')).toBeInTheDocument()
  })

  it('filters by search query', async () => {
    mockGoats()
    const user = userEvent.setup()
    renderList()
    await screen.findByText('G-002')
    await user.type(screen.getByRole('searchbox'), 'Daisy')
    expect(await screen.findByText('G-001')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.queryByText('G-002')).not.toBeInTheDocument(),
    )
  })

  it('filters by status', async () => {
    mockGoats()
    const user = userEvent.setup()
    renderList()
    await screen.findByText('G-001')
    await user.selectOptions(screen.getByLabelText(/status/i), 'sold')
    expect(await screen.findByText('G-002')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.queryByText('G-001')).not.toBeInTheDocument(),
    )
  })

  it('shows an empty state when no goats match', async () => {
    mockGoats([])
    renderList()
    expect(await screen.findByText(/no goats/i)).toBeInTheDocument()
  })
})
