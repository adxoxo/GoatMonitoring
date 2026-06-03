// Goat API calls. All HTTP for goats lives here — components/hooks import these.
import { client } from '@/api/client'

export async function getGoatProfile(uuid) {
  const { data } = await client.get(`/goats/${uuid}/`)
  return data
}

export async function listGoats(params = {}) {
  const { data } = await client.get('/goats/', { params })
  return data.results
}

export async function transferGoat(uuid, { target_area_id, reason = '' }) {
  const { data } = await client.post(`/goats/${uuid}/transfer/`, {
    target_area_id,
    reason,
  })
  return data
}
