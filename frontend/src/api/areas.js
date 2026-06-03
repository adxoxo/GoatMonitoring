// Area (pen) API calls.
import { client } from '@/api/client'

export async function listAreas() {
  const { data } = await client.get('/areas/')
  return data.results
}
