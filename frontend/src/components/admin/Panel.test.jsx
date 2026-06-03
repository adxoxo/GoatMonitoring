import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'

import Panel from '@/components/admin/Panel'

describe('Panel', () => {
  it('renders the title and children', () => {
    render(
      <Panel title="Alerts">
        <p>body</p>
      </Panel>,
    )
    expect(screen.getByText('Alerts')).toBeInTheDocument()
    expect(screen.getByText('body')).toBeInTheDocument()
  })
})
