// Goat API calls. All HTTP for goats lives here — components/hooks import these.
import { client } from '@/api/client'

export async function getGoatProfile(uuid) {
  const { data } = await client.get(`/goats/${uuid}/`)
  return data
}
