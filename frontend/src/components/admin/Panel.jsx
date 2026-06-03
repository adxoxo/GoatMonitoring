// Bordered panel with a design-system header (mono 10px uppercase, faint leather
// fill + bottom border). CLAUDE.md "Panel headers".
export default function Panel({ title, children }) {
  return (
    <section className="rounded-[3px] border border-leather/20 bg-paper">
      <h2 className="border-b border-leather/15 bg-leather/[0.04] px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-leather">
        {title}
      </h2>
      <div className="p-3">{children}</div>
    </section>
  )
}
