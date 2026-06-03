import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { makeQueryClient } from '@/tests/utils'
import Login from '@/pages/Login'

const TOKEN_URL = 'http://goatfarm.local/api/v1/auth/token/'

function renderLogin() {
  render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<div>DASH OK</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return userEvent.setup()
}

describe('Login page', () => {
  it('renders username, password, and submit', () => {
    renderLogin()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in|log in/i })).toBeInTheDocument()
  })

  it('logs in and navigates to the dashboard', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ access: 'a', refresh: 'r' }),
      ),
    )
    const user = renderLogin()
    await user.type(screen.getByLabelText(/username/i), 'owner')
    await user.type(screen.getByLabelText(/password/i), 'pw')
    await user.click(screen.getByRole('button', { name: /sign in|log in/i }))
    expect(await screen.findByText('DASH OK')).toBeInTheDocument()
  })

  it('shows an error on invalid credentials', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ detail: 'No active account' }, { status: 401 }),
      ),
    )
    const user = renderLogin()
    await user.type(screen.getByLabelText(/username/i), 'owner')
    await user.type(screen.getByLabelText(/password/i), 'bad')
    await user.click(screen.getByRole('button', { name: /sign in|log in/i }))
    expect(await screen.findByText(/incorrect|invalid|could not|failed/i)).toBeInTheDocument()
  })
})
