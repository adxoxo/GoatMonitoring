import { useParams } from 'react-router-dom'

// Public QR-scan landing page. Mobile-first, no admin chrome.
// Profile, health status, and the quick-log form arrive in Phases 2 & 4.
export default function GoatProfile() {
  const { uuid } = useParams()

  return (
    <main className="mx-auto min-h-svh max-w-[420px] px-4 py-8">
      <p className="font-mono text-[11px] uppercase tracking-wider text-rust">
        Worker view
      </p>
      <h1 className="mt-1 font-heading text-[26px] font-bold leading-tight text-soil">
        Goat profile
      </h1>
      <p className="mt-4 break-all font-mono text-xs text-leather">
        UUID: {uuid}
      </p>
      <p className="mt-4 text-sm leading-relaxed text-leather">
        Scanning a goat&apos;s ear-tag QR opens this page. The profile, health
        status, overdue banner, and quick health-log form are built in Phases 2
        and 4.
      </p>
    </main>
  )
}
