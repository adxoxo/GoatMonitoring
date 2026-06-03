import { useParams } from 'react-router-dom'
import {
  IconAlertTriangle,
  IconCalendar,
  IconHeartbeat,
  IconMapPin,
} from '@tabler/icons-react'

import { useGoatProfile } from '@/hooks/useGoatProfile'

// Public QR-scan landing page. Mobile-first, no admin chrome (CLAUDE.md design
// system: flat design, warm earth tones, readable at arm's length outdoors).
export default function GoatProfile() {
  const { uuid } = useParams()
  const { data: goat, isLoading, isError, error } = useGoatProfile(uuid)

  if (isLoading) return <ProfileSkeleton />
  if (isError) return <ProfileError status={error?.response?.status} />

  const sexTone =
    goat.sex_display === 'Female'
      ? 'bg-moss/15 text-moss border-moss/40'
      : 'bg-sky/15 text-sky border-sky/40'

  return (
    <main className="mx-auto min-h-svh max-w-[420px] px-4 py-6">
      <header className="flex items-baseline justify-between">
        <span className="font-heading text-[13px] font-bold text-leather">
          Goated<span className="text-clay">Tracking</span>
        </span>
        <span className="font-mono text-[22px] leading-none text-clay">
          {goat.tag_number}
        </span>
      </header>

      {goat.is_overdue && (
        <div
          role="alert"
          className="mt-4 flex items-center gap-2 border-l-[3px] border-alert bg-alert/10 px-3 py-2"
        >
          <IconAlertTriangle
            size={18}
            className="shrink-0 text-alert"
            aria-hidden
          />
          <span className="font-mono text-[11px] uppercase tracking-wide text-alert">
            Health record overdue
          </span>
        </div>
      )}

      <h1 className="mt-4 font-heading text-[26px] font-bold leading-tight text-soil">
        {goat.name || 'Unnamed goat'}
      </h1>

      <div className="mt-3 flex flex-wrap gap-2">
        <Badge className={sexTone}>{goat.sex_display}</Badge>
        {goat.current_area_name && (
          <Badge className="border-leather/30 bg-leather/10 text-leather">
            <IconMapPin size={12} aria-hidden /> {goat.current_area_name}
          </Badge>
        )}
        <Badge className="border-leather/30 bg-leather/10 text-leather">
          <IconCalendar size={12} aria-hidden /> {goat.age_display}
        </Badge>
      </div>

      <dl className="mt-5 divide-y divide-leather/10 rounded-[3px] bg-linen">
        <Field label="Status" value={goat.status_display} />
        <Field label="Sex" value={goat.sex_display} />
        <Field label="Age" value={goat.age_display} />
        <Field label="Area" value={goat.current_area_name || '—'} />
      </dl>

      <section className="mt-6">
        <h2 className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Recent health
        </h2>
        {goat.recent_health.length === 0 ? (
          <p className="mt-2 text-sm text-leather">No health records yet.</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {goat.recent_health.map((record) => (
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
      </section>
    </main>
  )
}

function Badge({ className = '', children }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-[2px] border px-2 py-0.5 font-mono text-[9.5px] uppercase tracking-wide ${className}`}
    >
      {children}
    </span>
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

function ProfileSkeleton() {
  return (
    <main
      data-testid="profile-skeleton"
      className="mx-auto min-h-svh max-w-[420px] animate-pulse px-4 py-6"
    >
      <div className="flex justify-between">
        <div className="h-4 w-28 rounded bg-leather/15" />
        <div className="h-6 w-20 rounded bg-clay/20" />
      </div>
      <div className="mt-5 h-7 w-2/3 rounded bg-leather/15" />
      <div className="mt-4 h-32 rounded-[3px] bg-linen" />
    </main>
  )
}

function ProfileError({ status }) {
  const message =
    status === 404
      ? 'Goat not found. Check the QR tag.'
      : 'Cannot load this goat. Check the WiFi connection and try again.'
  return (
    <main className="mx-auto grid min-h-svh max-w-[420px] place-items-center px-4 py-6">
      <div className="text-center">
        <IconAlertTriangle size={32} className="mx-auto text-alert" aria-hidden />
        <p className="mt-3 font-heading text-lg font-bold text-soil">{message}</p>
      </div>
    </main>
  )
}
