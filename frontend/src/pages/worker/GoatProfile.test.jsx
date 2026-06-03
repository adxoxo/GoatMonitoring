import { describe, expect, it } from 'vitest'
import { screen } from '@testing-library/react'
import { http, HttpResponse, delay } from 'msw'

import { server } from '@/tests/server'
import { renderAtRoute } from '@/tests/utils'
import GoatProfile from '@/pages/worker/GoatProfile'

const PROFILE_URL = 'http://goatfarm.local/api/v1/goats/:uuid/'

const baseProfile = {
  id: 'uuid-1',
  tag_number: 'G-042',
  name: 'Daisy',
  sex_display: 'Female',
  age_display: '2y 3m',
  status: 'active',
  status_display: 'Active',
  current_area_name: 'Pen A',
  qr_image_url: null,
  is_overdue: false,
  recent_health: [],
}

function mockProfile(overrides = {}) {
  server.use(
    http.get(PROFILE_URL, () =>
      HttpResponse.json({ ...baseProfile, ...overrides }),
    ),
  )
}

function renderProfile() {
  return renderAtRoute(<GoatProfile />, { path: '/g/:uuid', entry: '/g/uuid-1' })
}

describe('GoatProfile (worker view)', () => {
  it('renders goat name and tag number', async () => {
    mockProfile()
    renderProfile()
    expect(await screen.findByText('Daisy')).toBeInTheDocument()
    expect(screen.getByText('G-042')).toBeInTheDocument()
  })

  it('shows an overdue banner when the goat is overdue', async () => {
    mockProfile({ is_overdue: true })
    renderProfile()
    expect(await screen.findByText(/overdue/i)).toBeInTheDocument()
  })

  it('does not show an overdue banner when not overdue', async () => {
    mockProfile({ is_overdue: false })
    renderProfile()
    await screen.findByText('Daisy')
    expect(screen.queryByText(/overdue/i)).not.toBeInTheDocument()
  })

  it('shows a loading skeleton while fetching', async () => {
    server.use(
      http.get(PROFILE_URL, async () => {
        await delay(50)
        return HttpResponse.json(baseProfile)
      }),
    )
    renderProfile()
    expect(screen.getByTestId('profile-skeleton')).toBeInTheDocument()
    await screen.findByText('Daisy')
  })

  it('shows an error message on 404', async () => {
    server.use(
      http.get(PROFILE_URL, () =>
        HttpResponse.json({ detail: 'Not found.' }, { status: 404 }),
      ),
    )
    renderProfile()
    expect(await screen.findByText(/not found/i)).toBeInTheDocument()
  })
})
