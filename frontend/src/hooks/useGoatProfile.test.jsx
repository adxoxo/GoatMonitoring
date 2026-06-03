import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import { useGoatProfile } from '@/hooks/useGoatProfile'

const PROFILE_URL = 'http://goatfarm.local/api/v1/goats/:uuid/'

describe('useGoatProfile', () => {
  it('returns goat profile data', async () => {
    server.use(
      http.get(PROFILE_URL, () =>
        HttpResponse.json({ id: 'abc', tag_number: 'G-1', name: 'Daisy' }),
      ),
    )
    const { result } = renderHook(() => useGoatProfile('abc'), {
      wrapper: createWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data.tag_number).toBe('G-1')
  })

  it('handles 404 gracefully', async () => {
    server.use(
      http.get(PROFILE_URL, () =>
        HttpResponse.json({ detail: 'Not found.' }, { status: 404 }),
      ),
    )
    const { result } = renderHook(() => useGoatProfile('missing'), {
      wrapper: createWrapper(),
    })
    await waitFor(() => expect(result.current.isError).toBe(true))
  })
})
