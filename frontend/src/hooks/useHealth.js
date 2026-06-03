// React Query hooks for health records, alerts, and the worker quick-log.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getAlerts, listHealthRecords, logHealthEntry } from '@/api/health'

export function useHealthRecords(params = {}) {
  return useQuery({
    queryKey: ['health', params],
    queryFn: () => listHealthRecords(params),
  })
}

export function useAlerts() {
  return useQuery({ queryKey: ['alerts'], queryFn: getAlerts })
}

// On success, refresh the goat profile (recent_health / is_overdue change) + alerts.
export function useLogHealthEntry(uuid) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (entry) => logHealthEntry(uuid, entry),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goat-profile', uuid] })
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })
}
