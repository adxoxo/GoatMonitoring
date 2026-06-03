import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import Areas from '@/pages/admin/Areas'

const AREAS_URL = 'http://goatfarm.local/api/v1/areas/'
const GOATS_URL = 'http://goatfarm.local/api/v1/goats/'

function mockData() {
  server.use(
    http.get(AREAS_URL, () =>
      HttpResponse.json({
        count: 2,
        results: [
          { id: 'a1', name: 'Pen A — Does', capacity: 20, goat_count: 12 },
          { id: 'a2', name: 'Quarantine', capacity: 5, goat_count: 0 },
        ],
      }),
    ),
    http.get(GOATS_URL, () => HttpResponse.json({ count: 0, results: [] })),
  )
}

function renderAreas() {
  const Wrapper = createWrapper()
  render(
    <Wrapper>
      <Areas />
    </Wrapper>,
  )
}

describe('Areas page', () => {
  it('renders a card for each pen with its goat count and capacity', async () => {
    mockData()
    renderAreas()
    expect(
      await screen.findByRole('heading', { name: 'Pen A — Does' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Quarantine' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/12\s*\/\s*20/)).toBeInTheDocument()
  })
})
