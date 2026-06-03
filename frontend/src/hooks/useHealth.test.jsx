import { describe, expect, it } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'

import { server } from '@/tests/server'
import { createWrapper } from '@/tests/utils'
import { useAlerts, useHealthRecords, useLogHealthEntry } from '@/hooks/useHealth'

const HEALTH_URL = 'http://goatfarm.local/api/v1/health/'
const ALERTS_URL = 'http://goatfarm.local/api/v1/alerts/'
const LOG_URL = 'http://goatfarm.local/api/v1/goats/:uuid/log/'

describe('useHealth hooks', () => {
  it('useHealthRecords returns records', async () => {
    server.use(
      http.get(HEALTH_URL, () =>
        HttpResponse.json({
          count: 1,
          results: [{ id: 'h1', record_type_display: 'Checkup' }],
        }),
      ),
    )
    const { result } = renderHook(() => useHealthRecords(), {
      wrapper: createWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data[0].record_type_display).toBe('Checkup')
  })

  it('useAlerts returns the feed object', async () => {
    server.use(
      http.get(ALERTS_URL, () =>
        HttpResponse.json({ overdue: [{ id: 'h1' }], due_soon: [] }),
      ),
    )
    const { result } = renderHook(() => useAlerts(), { wrapper: createWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data.overdue).toHaveLength(1)
  })

  it('useLogHealthEntry posts a worker log entry', async () => {
    server.use(
      http.post(LOG_URL, () =>
        HttpResponse.json({ id: 'h2', record_type: 'note' }, { status: 201 }),
      ),
    )
    const { result } = renderHook(() => useLogHealthEntry('uuid-1'), {
      wrapper: createWrapper(),
    })
    result.current.mutate({ record_type: 'note', description: 'Limping' })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
  })
})
