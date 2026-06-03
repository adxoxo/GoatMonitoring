// QR tag API calls.
import { client } from '@/api/client'

// Generate or regenerate a goat's QR tag (admin). Old tag is deactivated
// server-side; returns the new active QRCode record.
export async function regenerateQrTag(uuid) {
  const { data } = await client.post(`/goats/${uuid}/qr/`)
  return data
}
