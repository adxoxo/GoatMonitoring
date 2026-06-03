import { describe, expect, it } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import TransferForm from '@/components/admin/TransferForm'

const TRANSFER_URL = 'http://goatfarm.local/api/v1/goats/:uuid/transfer/'

const goats = [{ id: 'g1', tag_number: 'G-1', name: 'Daisy' }]
const areas = [
  { id: 'a1', name: 'Pen A', capacity: 20, goat_count: 2 },
  { id: 'a2', name: 'Quarantine', capacity: 5, goat_count: 0 },
]

function renderForm() {
  const Wrapper = createWrapper()
  render(
    <Wrapper>
      <TransferForm goats={goats} areas={areas} />
    </Wrapper>,
  )
  return { user: userEvent.setup() }
}

describe('TransferForm', () => {
  it('shows a risk warning when the transfer returns a non-NONE risk', async () => {
    server.use(
      http.post(TRANSFER_URL, () =>
        HttpResponse.json({
          goat: { id: 'g1', tag_number: 'G-1' },
          risk_level: 'closely_related',
          risk_level_display: 'Closely related',
          related_goats: [{ id: 'g9', tag_number: 'G-9', name: 'Buck' }],
          transfer_log: { id: 'l1' },
        }),
      ),
    )
    const { user } = renderForm()
    await user.selectOptions(screen.getByLabelText(/goat/i), 'g1')
    await user.selectOptions(screen.getByLabelText(/destination/i), 'a1')
    await user.click(screen.getByRole('button', { name: /transfer/i }))
    expect(await screen.findByText(/closely related/i)).toBeInTheDocument()
  })

  it('submits the transfer without blocking on a warning (advisory only)', async () => {
    let called = false
    server.use(
      http.post(TRANSFER_URL, () => {
        called = true
        return HttpResponse.json({
          goat: { id: 'g1', tag_number: 'G-1' },
          risk_level: 'none',
          risk_level_display: 'None',
          related_goats: [],
          transfer_log: { id: 'l1' },
        })
      }),
    )
    const { user } = renderForm()
    await user.selectOptions(screen.getByLabelText(/goat/i), 'g1')
    await user.selectOptions(screen.getByLabelText(/destination/i), 'a2')
    await user.click(screen.getByRole('button', { name: /transfer/i }))
    await waitFor(() => expect(called).toBe(true))
  })
})
