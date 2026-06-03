import { useState } from 'react'
import { IconAlertTriangle } from '@tabler/icons-react'

import { useTransferGoat } from '@/hooks/useAreas'

// Move a goat to another area. The lineage risk is advisory — the transfer
// always proceeds; a warning banner appears afterward if risk is non-NONE.
export default function TransferForm({ goats = [], areas = [] }) {
  const [goatId, setGoatId] = useState('')
  const [areaId, setAreaId] = useState('')
  const [reason, setReason] = useState('')
  const transfer = useTransferGoat()

  const result = transfer.data
  const showWarning = result && result.risk_level !== 'none'

  function handleSubmit(event) {
    event.preventDefault()
    if (!goatId || !areaId) return
    transfer.mutate({ uuid: goatId, target_area_id: areaId, reason })
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-[3px] bg-linen p-4">
      <h2 className="font-mono text-[10px] uppercase tracking-wider text-leather">
        Transfer a goat
      </h2>

      <label className="mt-3 block text-xs text-leather" htmlFor="transfer-goat">
        Goat
      </label>
      <select
        id="transfer-goat"
        value={goatId}
        onChange={(e) => setGoatId(e.target.value)}
        className="mt-1 w-full cursor-pointer rounded-[3px] border border-leather/30 bg-paper px-2 py-1.5 text-sm"
      >
        <option value="">Select a goat…</option>
        {goats.map((g) => (
          <option key={g.id} value={g.id}>
            {g.tag_number}
            {g.name ? ` — ${g.name}` : ''}
          </option>
        ))}
      </select>

      <label className="mt-3 block text-xs text-leather" htmlFor="transfer-area">
        Destination area
      </label>
      <select
        id="transfer-area"
        value={areaId}
        onChange={(e) => setAreaId(e.target.value)}
        className="mt-1 w-full cursor-pointer rounded-[3px] border border-leather/30 bg-paper px-2 py-1.5 text-sm"
      >
        <option value="">Select an area…</option>
        {areas.map((a) => (
          <option key={a.id} value={a.id}>
            {a.name}
          </option>
        ))}
      </select>

      <label className="mt-3 block text-xs text-leather" htmlFor="transfer-reason">
        Reason
      </label>
      <input
        id="transfer-reason"
        type="text"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        className="mt-1 w-full rounded-[3px] border border-leather/30 bg-paper px-2 py-1.5 text-sm"
      />

      <button
        type="submit"
        disabled={transfer.isPending}
        className="mt-4 w-full cursor-pointer rounded-[3px] bg-clay px-3 py-2 font-mono text-[11px] uppercase tracking-wide text-paper hover:bg-clay/90 disabled:opacity-50"
      >
        {transfer.isPending ? 'Transferring…' : 'Transfer'}
      </button>

      {showWarning && (
        <div
          role="alert"
          className="mt-4 border-l-[3px] border-warn bg-warn/10 px-3 py-2"
        >
          <p className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wide text-warn">
            <IconAlertTriangle size={16} aria-hidden /> {result.risk_level_display}
          </p>
          <p className="mt-1 text-xs text-leather">
            Moved anyway (advisory). Related goats already here:{' '}
            {result.related_goats.map((g) => g.tag_number).join(', ')}
          </p>
        </div>
      )}

      {result && !showWarning && (
        <p className="mt-3 font-mono text-[11px] text-ok">Transfer complete.</p>
      )}
    </form>
  )
}
