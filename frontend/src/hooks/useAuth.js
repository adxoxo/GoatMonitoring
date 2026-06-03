// Auth: login mutation (stores JWT in localStorage) + logout + token helpers.
// The axios client reads access_token from localStorage on every request.
import { useMutation } from '@tanstack/react-query'

import { login } from '@/api/auth'

export function useLogin() {
  return useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access)
      if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
    },
  })
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'))
}
