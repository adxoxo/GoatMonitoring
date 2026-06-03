// Single axios instance for all API calls. Base URL points at the local farm
// server in production; tests run against this host via MSW.
import axios from 'axios'

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://goatfarm.local/api/v1'

export const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach the admin JWT (when present) to outgoing requests. The login flow
// that stores this token arrives later; public worker endpoints work without it.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
