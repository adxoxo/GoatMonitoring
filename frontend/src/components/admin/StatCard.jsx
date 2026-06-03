// Dashboard/health stat card: linen fill, 2px colored bottom bar (not an icon),
// Syne value, mono label. Design system — CLAUDE.md "Stat cards".
const BARS = {
  ok: 'bg-ok',
  warn: 'bg-warn',
  alert: 'bg-alert',
  neutral: 'bg-leather/20',
}

export default function StatCard({ label, value, tone = 'neutral' }) {
  return (
    <div className="relative overflow-hidden rounded-[3px] border border-leather/20 bg-linen p-4">
      <p className="font-heading text-[28px] font-bold leading-none tracking-[-0.03em] text-soil">
        {value}
      </p>
      <p className="mt-2 font-mono text-[9px] uppercase tracking-wider text-rust">
        {label}
      </p>
      <span
        className={`absolute inset-x-0 bottom-0 h-0.5 ${BARS[tone] ?? BARS.neutral}`}
        aria-hidden
      />
    </div>
  )
}
