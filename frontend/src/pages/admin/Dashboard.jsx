import { useNavigate } from 'react-router-dom'
import { IconHeartbeat } from '@tabler/icons-react'

import { useDashboard } from '@/hooks/useDashboard'
import StatCard from '@/components/admin/StatCard'
import Badge from '@/components/admin/Badge'
import Panel from '@/components/admin/Panel'

export default function Dashboard() {
  const navigate = useNavigate()
  const { goats, recent, alerts, stats, isLoading } = useDashboard()

  return (
    <div className="p-6">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Overview
        </p>
        <h1 className="font-heading text-2xl font-bold text-soil">Dashboard</h1>
      </header>

      <div
        data-testid="stat-cards"
        className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
      >
        <StatCard label="Total goats" value={stats.totalGoats} tone="neutral" />
        <StatCard label="Overdue" value={stats.overdue} tone="alert" />
        <StatCard label="Due this week" value={stats.dueThisWeek} tone="warn" />
        <StatCard label="Active pens" value={stats.activePens} tone="neutral" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <Panel title="Alerts">
            <AlertsList alerts={alerts} onOpen={(id) => navigate(`/goats/${id}`)} />
          </Panel>
        </div>
        <div className="lg:col-span-2">
          <Panel title="Recent activity">
            {recent.length === 0 ? (
              <p className="text-sm text-leather">No recent activity.</p>
            ) : (
              <ul className="space-y-2">
                {recent.map((record) => (
                  <li
                    key={record.id}
                    className="flex items-center gap-3 rounded-[3px] bg-linen px-3 py-2"
                  >
                    <span className="grid size-[30px] shrink-0 place-items-center rounded-[4px] bg-sage/20 text-sage">
                      <IconHeartbeat size={16} aria-hidden />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium text-soil">
                        {record.record_type_display}
                      </span>
                      <span className="font-mono text-[10px] text-rust">
                        {record.record_date}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>
      </div>

      <section className="mt-6">
        <h2 className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Herd overview
        </h2>
        <div className="mt-2 overflow-x-auto">
          {isLoading ? (
            <p className="text-sm text-leather">Loading…</p>
          ) : goats.length === 0 ? (
            <p className="text-sm text-leather">No goats yet.</p>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-leather/35 bg-leather/5 text-left">
                  {['Tag', 'Name', 'Sex', 'Area', 'Status'].map((h) => (
                    <th
                      key={h}
                      className="px-3 py-2 font-mono text-[9px] uppercase tracking-wider text-rust"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {goats.map((goat) => (
                  <tr
                    key={goat.id}
                    onClick={() => navigate(`/goats/${goat.id}`)}
                    className="cursor-pointer border-b border-leather/10 hover:bg-leather/[0.03]"
                  >
                    <td className="px-3 py-2 font-mono text-[11px] text-leather">
                      {goat.tag_number}
                    </td>
                    <td className="px-3 py-2 text-sm text-soil">{goat.name}</td>
                    <td className="px-3 py-2">
                      <Badge tone={goat.sex_display === 'Female' ? 'female' : 'male'}>
                        {goat.sex_display}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-sm text-leather">
                      {goat.current_area_name || '—'}
                    </td>
                    <td className="px-3 py-2">
                      <Badge tone={goat.status === 'active' ? 'ok' : 'neutral'}>
                        {goat.status_display}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  )
}

function AlertsList({ alerts, onOpen }) {
  const rows = [
    ...alerts.overdue.map((r) => ({ ...r, tone: 'alert' })),
    ...alerts.due_soon.map((r) => ({ ...r, tone: 'warn' })),
  ]
  if (rows.length === 0) {
    return <p className="text-sm text-leather">No alerts.</p>
  }
  return (
    <ul className="space-y-2">
      {rows.map((record) => (
        <li
          key={record.id}
          onClick={() => onOpen(record.goat)}
          className={`flex cursor-pointer items-center justify-between border-l-[3px] px-3 py-2 ${
            record.tone === 'alert'
              ? 'border-alert bg-alert/10'
              : 'border-warn bg-warn/10'
          }`}
        >
          <span className="font-mono text-[11px] text-leather">
            {record.goat_tag_number}
          </span>
          <Badge tone={record.status}>{record.status}</Badge>
        </li>
      ))}
    </ul>
  )
}
