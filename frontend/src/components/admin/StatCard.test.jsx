import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import StatCard from '@/components/admin/StatCard'

describe('StatCard', () => {
  it('renders value and label', () => {
    render(<StatCard label="Overdue" value={3} />)
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('Overdue')).toBeInTheDocument()
  })

  it('applies the alert tone bottom bar', () => {
    const { container } = render(<StatCard label="Overdue" value={3} tone="alert" />)
    expect(container.querySelector('.bg-alert')).toBeTruthy()
  })
})
