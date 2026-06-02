import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect } from 'vitest'

import App from '@/App'
import GoatProfile from '@/pages/worker/GoatProfile'

describe('Phase 0 scaffold', () => {
  it('boots the admin shell and lands on the dashboard', () => {
    render(<App />)
    // Sidebar logo sub-label is unique to the shell.
    expect(screen.getByText('Farm OS v1.0')).toBeInTheDocument()
  })

  it('worker profile route reads the goat UUID from the URL', () => {
    render(
      <MemoryRouter initialEntries={['/g/abc-123-uuid']}>
        <Routes>
          <Route path="/g/:uuid" element={<GoatProfile />} />
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText(/abc-123-uuid/)).toBeInTheDocument()
  })
})
