// Health record + alert API calls. All HTTP for health lives here.
import { client } from '@/api/client'

// Worker quick-log (public, no auth — VITE_WORKER_AUTH_ENABLED=false).
// POST /api/v1/goats/{uuid}/log/ — server timestamps the entry.
export async function logHealthEntry(uuid, { record_type, description = '' }) {
  const { data } = await client.post(`/goats/${uuid}/log/`, {
    record_type,
    description,
  })
  return data
}

// Admin health-records feed. GET /api/v1/health/?record_type=&goat=
export async function listHealthRecords(params = {}) {
  const { data } = await client.get('/health/', { params })
  return data.results
}

// Overdue + upcoming alerts. GET /api/v1/alerts/ → { overdue, due_soon }
export async function getAlerts() {
  const { data } = await client.get('/alerts/')
  return data
}
