// Mutation hook: regenerate a goat's QR tag, then refresh its profile.
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { regenerateQrTag } from '@/api/qr'

export function useRegenerateQr(uuid) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => regenerateQrTag(uuid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goat-profile', uuid] })
    },
  })
}
