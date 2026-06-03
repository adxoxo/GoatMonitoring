import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import QrTagCard from '@/components/admin/QrTagCard'

describe('QrTagCard', () => {
  it('renders the QR image when a url is available', () => {
    render(
      <QrTagCard uuid="uuid-1" qrImageUrl="/media/qr/uuid-1.png" onRegenerate={() => {}} />,
    )
    const img = screen.getByRole('img', { name: /qr/i })
    expect(img).toHaveAttribute('src', '/media/qr/uuid-1.png')
  })

  it('shows a placeholder when there is no QR yet', () => {
    render(<QrTagCard uuid="uuid-1" qrImageUrl={null} onRegenerate={() => {}} />)
    expect(screen.getByText(/no qr/i)).toBeInTheDocument()
  })

  it('opens the QR image in a new tab when Print is clicked', async () => {
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => {})
    render(
      <QrTagCard uuid="uuid-1" qrImageUrl="/media/qr/uuid-1.png" onRegenerate={() => {}} />,
    )
    await userEvent.click(screen.getByRole('button', { name: /print/i }))
    expect(openSpy).toHaveBeenCalledWith('/media/qr/uuid-1.png', '_blank')
    openSpy.mockRestore()
  })

  it('calls onRegenerate when Regenerate is clicked', async () => {
    const onRegenerate = vi.fn()
    render(
      <QrTagCard uuid="uuid-1" qrImageUrl="/media/qr/uuid-1.png" onRegenerate={onRegenerate} />,
    )
    await userEvent.click(screen.getByRole('button', { name: /regenerate/i }))
    expect(onRegenerate).toHaveBeenCalledTimes(1)
  })
})
