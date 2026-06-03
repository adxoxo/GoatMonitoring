// Square status/sex badge (border-radius 2px, mono 9.5px). The `tone` is chosen
// by the caller from serializer-provided data — the component never classifies.
const TONES = {
  overdue: 'bg-alert/15 text-alert border-alert/40',
  due_soon: 'bg-warn/15 text-warn border-warn/40',
  on_schedule: 'bg-ok/15 text-ok border-ok/40',
  ok: 'bg-ok/15 text-ok border-ok/40',
  female: 'bg-moss/15 text-moss border-moss/40',
  male: 'bg-sky/15 text-sky border-sky/40',
  neutral: 'bg-leather/10 text-leather border-leather/30',
}

export default function Badge({ tone = 'neutral', children }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-[2px] border px-2 py-0.5 font-mono text-[9.5px] uppercase tracking-wide ${
        TONES[tone] ?? TONES.neutral
      }`}
    >
      {children}
    </span>
  )
}
