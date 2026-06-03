import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAlerts, useHealthRecords } from '@/hooks/useHealth'
import StatCard from '@/components/admin/StatCard'
import Badge from '@/components/admin/Badge'

const TABS = [
  { key: '', label: 'All' },
  { key: 'vaccination', label: 'Vaccination' },
  { key: 'deworming', label: 'Deworming' },
  { key: 'checkup', label: 'Checkup' },
]

export default function HealthRecords() {
  const [filter, setFilter] = useState('')
  const navigate = useNavigate()
  const { data: records = [], isLoading } = useHealthRecords({
    record_type: filter || undefined,
  })
  const { data: alerts } = useAlerts()

  return (
    <div className="p-6">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Health
        </p>
        <h1 className="font-heading text-2xl font-bold text-soil">Health Records</h1>
      </header>

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total records" value={records.length} tone="neutral" />
        <StatCard
          label="Due this week"
          value={alerts?.due_soon.length ?? 0}
          tone="warn"
        />
        <StatCard label="Overdue" value={alerts?.overdue.length ?? 0} tone="alert" />
        <StatCard label="On schedule" value={records.length} tone="ok" />
      </div>

      <div className="mt-6 flex gap-1 border-b border-leather/20">
        {TABS.map((tab) => (
          <button
            key={tab.key || 'all'}
            type="button"
            onClick={() => setFilter(tab.key)}
            className={`cursor-pointer border-b-2 px-3 py-2 font-mono text-[10px] uppercase tracking-wide ${
              filter === tab.key
                ? 'border-clay text-clay'
                : 'border-transparent text-rust hover:text-leather'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-4 overflow-x-auto">
        {isLoading ? (
          <p className="text-sm text-leather">Loading…</p>
        ) : records.length === 0 ? (
          <p className="text-sm text-leather">No records.</p>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-leather/35 bg-leather/5 text-left">
                {['Tag', 'Type', 'Date', 'Next due', 'Status'].map((h) => (
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
              {records.map((record) => (
                <tr
                  key={record.id}
                  onClick={() => navigate(`/goats/${record.goat}`)}
                  className="cursor-pointer border-b border-leather/10 hover:bg-leather/[0.03]"
                >
                  <td className="px-3 py-2 font-mono text-[11px] text-leather">
                    {record.goat_tag_number}
                  </td>
                  <td className="px-3 py-2 text-sm text-soil">
                    {record.record_type_display}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-leather">
                    {record.record_date}
                  </td>
                  <td className="px-3 py-2 font-mono text-[11px] text-leather">
                    {record.next_due_date || '—'}
                  </td>
                  <td className="px-3 py-2">
                    <Badge tone={record.status}>{record.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
