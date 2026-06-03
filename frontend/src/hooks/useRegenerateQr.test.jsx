import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import { useRegenerateQr } from '@/hooks/useRegenerateQr'

const QR_URL = 'http://goatfarm.local/api/v1/goats/:uuid/qr/'

describe('useRegenerateQr', () => {
  it('posts to the regenerate endpoint and resolves', async () => {
    server.use(
      http.post(QR_URL, () =>
        HttpResponse.json(
          { id: 'qr-2', goat: 'uuid-1', image_path: 'qr/uuid-1.png', is_active: true },
          { status: 201 },
        ),
      ),
    )
    const { result } = renderHook(() => useRegenerateQr('uuid-1'), {
      wrapper: createWrapper(),
    })
    result.current.mutate()
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data.is_active).toBe(true)
  })
})
