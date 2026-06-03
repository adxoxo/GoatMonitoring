// Admin auth API — JWT obtain (login).
import { client } from '@/api/client'

export async function login({ username, password }) {
  const { data } = await client.post('/auth/token/', { username, password })
  return data // { access, refresh }
}
