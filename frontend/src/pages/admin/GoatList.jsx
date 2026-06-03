import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useGoats } from '@/hooks/useAreas'
import Badge from '@/components/admin/Badge'

const STATUSES = [
  { key: '', label: 'All statuses' },
  { key: 'active', label: 'Active' },
  { key: 'quarantined', label: 'Quarantined' },
  { key: 'sold', label: 'Sold' },
  { key: 'deceased', label: 'Deceased' },
]

export default function GoatList() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const navigate = useNavigate()
  const { data: goats = [], isLoading } = useGoats({
    search: search || undefined,
    status: status || undefined,
  })

  return (
    <div className="p-6">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Herd
        </p>
        <h1 className="font-heading text-2xl font-bold text-soil">Goats</h1>
      </header>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="search"
          aria-label="Search goats"
          placeholder="Search tag or name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-h-[40px] flex-1 rounded-[3px] border border-leather/30 bg-paper px-3 text-sm text-soil"
        />
        <select
          aria-label="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="min-h-[40px] cursor-pointer rounded-[3px] border border-leather/30 bg-paper px-3 text-sm text-soil"
        >
          {STATUSES.map((s) => (
            <option key={s.key || 'all'} value={s.key}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-4 overflow-x-auto">
        {isLoading ? (
          <p className="text-sm text-leather">Loading…</p>
        ) : goats.length === 0 ? (
          <p className="text-sm text-leather">No goats found.</p>
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
    </div>
  )
}
