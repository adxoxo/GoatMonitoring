import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import AppShell from '@/components/shared/AppShell'
import Dashboard from '@/pages/admin/Dashboard'
import GoatList from '@/pages/admin/GoatList'
import GoatDetail from '@/pages/admin/GoatDetail'
import Areas from '@/pages/admin/Areas'
import HealthRecords from '@/pages/admin/HealthRecords'
import GoatProfile from '@/pages/worker/GoatProfile'
import NotFound from '@/pages/NotFound'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Worker view — public QR-scan landing, no admin chrome */}
          <Route path="/g/:uuid" element={<GoatProfile />} />

          {/* Admin — wrapped in the dashboard shell */}
          <Route element={<AppShell />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/goats" element={<GoatList />} />
            <Route path="/goats/:uuid" element={<GoatDetail />} />
            <Route path="/areas" element={<Areas />} />
            <Route path="/health" element={<HealthRecords />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
