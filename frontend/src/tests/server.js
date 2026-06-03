// Mock Service Worker — intercepts API calls in tests.
// Per-test handlers are added with server.use(...).
import { setupServer } from 'msw/node'

export const server = setupServer()
