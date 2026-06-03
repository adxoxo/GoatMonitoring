// Single axios instance for all API calls. Base URL points at the local farm
// server in production; tests run against this host via MSW.
import axios from 'axios'

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://goatfarm.local/api/v1'

export const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})
