import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import LineageTree from '@/components/admin/LineageTree'

function renderTree(lineage) {
  render(
    <MemoryRouter>
      <LineageTree lineage={lineage} />
    </MemoryRouter>,
  )
}

describe('LineageTree', () => {
  it('renders the sire and dam tag numbers', () => {
    renderTree({
      sire: { id: 's1', tag_number: 'G-SIRE', name: 'Bolt' },
      dam: { id: 'd1', tag_number: 'G-DAM', name: 'Daisy' },
      paternal_grandsire: null,
      paternal_granddam: null,
      maternal_grandsire: null,
      maternal_granddam: null,
    })
    expect(screen.getByText('G-SIRE')).toBeInTheDocument()
    expect(screen.getByText('G-DAM')).toBeInTheDocument()
  })

  it('renders "Unknown" for a null parent', () => {
    renderTree({
      sire: null,
      dam: { id: 'd1', tag_number: 'G-DAM', name: 'Daisy' },
      paternal_grandsire: null,
      paternal_granddam: null,
      maternal_grandsire: null,
      maternal_granddam: null,
    })
    expect(screen.getAllByText(/unknown/i).length).toBeGreaterThan(0)
  })

  it('links a known parent to its profile', () => {
    renderTree({
      sire: { id: 's1', tag_number: 'G-SIRE', name: 'Bolt' },
      dam: null,
      paternal_grandsire: null,
      paternal_granddam: null,
      maternal_grandsire: null,
      maternal_granddam: null,
    })
    expect(screen.getByRole('link', { name: /G-SIRE/ })).toHaveAttribute(
      'href',
      '/goats/s1',
    )
  })
})
