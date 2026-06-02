// Phase 0 scaffold placeholder. Real pages replace these in Phases 2–4.
export default function PagePlaceholder({ eyebrow, title, children }) {
  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
        {eyebrow}
      </p>
      <h2 className="mt-1 font-heading text-2xl font-bold text-soil">{title}</h2>
      {children ? (
        <p className="mt-3 max-w-prose text-sm leading-relaxed text-leather">
          {children}
        </p>
      ) : null}
    </div>
  )
}
