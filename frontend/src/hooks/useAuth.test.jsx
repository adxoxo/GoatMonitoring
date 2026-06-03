import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import { useLogin } from '@/hooks/useAuth'

const TOKEN_URL = 'http://goatfarm.local/api/v1/auth/token/'

describe('useLogin', () => {
  it('stores the access token on success', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ access: 'tok-abc', refresh: 'tok-ref' }),
      ),
    )
    const { result } = renderHook(() => useLogin(), { wrapper: createWrapper() })
    result.current.mutate({ username: 'owner', password: 'pw' })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(localStorage.getItem('access_token')).toBe('tok-abc')
  })

  it('surfaces an error on bad credentials', async () => {
    server.use(
      http.post(TOKEN_URL, () =>
        HttpResponse.json({ detail: 'No active account' }, { status: 401 }),
      ),
    )
    const { result } = renderHook(() => useLogin(), { wrapper: createWrapper() })
    result.current.mutate({ username: 'owner', password: 'bad' })
    await waitFor(() => expect(result.current.isError).toBe(true))
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})
