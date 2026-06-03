import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import { useAreas } from '@/hooks/useAreas'

const AREAS_URL = 'http://goatfarm.local/api/v1/areas/'

describe('useAreas', () => {
  it('returns the list of areas', async () => {
    server.use(
      http.get(AREAS_URL, () =>
        HttpResponse.json({
          count: 1,
          results: [
            { id: 'a1', name: 'Pen A', capacity: 20, goat_count: 5 },
          ],
        }),
      ),
    )
    const { result } = renderHook(() => useAreas(), { wrapper: createWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toHaveLength(1)
    expect(result.current.data[0].name).toBe('Pen A')
  })
})
