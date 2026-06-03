import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import Badge from '@/components/admin/Badge'

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Active</Badge>)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('applies overdue tone classes', () => {
    render(<Badge tone="overdue">Overdue</Badge>)
    expect(screen.getByText('Overdue').className).toMatch(/text-alert/)
  })
})
