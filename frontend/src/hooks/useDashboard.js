// Dashboard data: composes goats + alerts + recent health into stat-card-ready
// counts. Derivation lives here, not in the component (no business logic in JSX).
import { useGoats } from '@/hooks/useAreas'
import { useAlerts, useHealthRecords } from '@/hooks/useHealth'

export function useDashboard() {
  const goatsQuery = useGoats()
  const alertsQuery = useAlerts()
  const recentQuery = useHealthRecords()

  const goats = goatsQuery.data ?? []
  const alerts = alertsQuery.data ?? { overdue: [], due_soon: [] }

  return {
    isLoading: goatsQuery.isLoading || alertsQuery.isLoading,
    goats,
    recent: recentQuery.data ?? [],
    alerts,
    stats: {
      totalGoats: goats.length,
      overdue: alerts.overdue.length,
      dueThisWeek: alerts.due_soon.length,
      activePens: new Set(
        goats.map((g) => g.current_area).filter(Boolean),
      ).size,
    },
  }
}
