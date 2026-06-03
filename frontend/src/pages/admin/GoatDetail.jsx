import { useParams } from 'react-router-dom'

import { useGoatProfile } from '@/hooks/useGoatProfile'
import { useRegenerateQr } from '@/hooks/useRegenerateQr'
import QrTagCard from '@/components/admin/QrTagCard'

// Admin goat detail. Phase 2 wires the identity header + QR tag block; the full
// lineage tree and health history arrive in Phases 3–4.
export default function GoatDetail() {
  const { uuid } = useParams()
  const { data: goat, isLoading, isError } = useGoatProfile(uuid)
  const regenerate = useRegenerateQr(uuid)

  if (isLoading) return <p className="p-6 text-sm text-leather">Loading…</p>
  if (isError)
    return <p className="p-6 text-sm text-alert">Could not load this goat.</p>

  return (
    <div className="mx-auto max-w-3xl p-6">
      <header className="flex items-baseline justify-between">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
            Goat
          </p>
          <h1 className="font-heading text-2xl font-bold text-soil">
            {goat.name || 'Unnamed goat'}
          </h1>
        </div>
        <span className="font-mono text-2xl text-clay">{goat.tag_number}</span>
      </header>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <dl className="divide-y divide-leather/10 rounded-[3px] bg-linen">
          <Field label="Status" value={goat.status_display} />
          <Field label="Sex" value={goat.sex_display} />
          <Field label="Age" value={goat.age_display} />
          <Field label="Area" value={goat.current_area_name || '—'} />
        </dl>

        <QrTagCard
          uuid={goat.id}
          qrImageUrl={goat.qr_image_url}
          onRegenerate={() => regenerate.mutate()}
          isRegenerating={regenerate.isPending}
        />
      </div>
    </div>
  )
}

function Field({ label, value }) {
  return (
    <div className="flex min-h-[44px] items-center justify-between px-3">
      <dt className="font-mono text-[10px] uppercase tracking-wider text-rust">
        {label}
      </dt>
      <dd className="text-sm text-soil">{value}</dd>
    </div>
  )
}
