// Vitest global setup. jest-dom adds matchers like toBeInTheDocument().
import '@testing-library/jest-dom'
import { afterAll, afterEach, beforeAll } from 'vitest'

import { server } from './server'

// MSW lifecycle — unhandled requests fail loudly so tests can't hit the network.
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  server.resetHandlers()
  localStorage.clear() // don't leak auth tokens between tests
})
afterAll(() => server.close())
