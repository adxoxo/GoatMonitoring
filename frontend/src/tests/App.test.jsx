import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

import App from '@/App'

describe('App shell', () => {
  it('boots the admin shell and lands on the dashboard', () => {
    render(<App />)
    // Sidebar logo sub-label is unique to the shell.
    expect(screen.getByText('Farm OS v1.0')).toBeInTheDocument()
  })
})

// The worker /g/:uuid route is covered by src/pages/worker/GoatProfile.test.jsx
// (it now fetches data and needs React Query + MSW).
