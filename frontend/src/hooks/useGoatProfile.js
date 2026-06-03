// React Query hook wrapping the public goat-profile fetch.
import { useQuery } from '@tanstack/react-query'

import { getGoatProfile } from '@/api/goats'

export function useGoatProfile(uuid) {
  return useQuery({
    queryKey: ['goat-profile', uuid],
    queryFn: () => getGoatProfile(uuid),
    enabled: Boolean(uuid),
  })
}
