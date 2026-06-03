// React Query hooks for areas (pens) and goat transfers.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { listAreas } from '@/api/areas'
import { listGoats, transferGoat } from '@/api/goats'

export function useAreas() {
  return useQuery({ queryKey: ['areas'], queryFn: listAreas })
}

export function useGoats(params = {}) {
  return useQuery({ queryKey: ['goats', params], queryFn: () => listGoats(params) })
}

export function useTransferGoat() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ uuid, ...data }) => transferGoat(uuid, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      queryClient.invalidateQueries({ queryKey: ['goats'] })
    },
  })
}
