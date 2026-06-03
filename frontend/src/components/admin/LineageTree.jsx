import { Link } from 'react-router-dom'

// Two-generation lineage: parents and grandparents. Unknown ancestors render
// as a muted "Unknown"; known ones link to that goat's detail page.
export default function LineageTree({ lineage }) {
  if (!lineage) return null
  return (
    <section className="rounded-[3px] border border-leather/20 bg-paper p-4">
      <h2 className="font-mono text-[10px] uppercase tracking-wider text-leather">
        Lineage
      </h2>

      <div className="mt-3 space-y-3">
        <ParentBranch
          label="Sire"
          parent={lineage.sire}
          grandsire={lineage.paternal_grandsire}
          granddam={lineage.paternal_granddam}
        />
        <ParentBranch
          label="Dam"
          parent={lineage.dam}
          grandsire={lineage.maternal_grandsire}
          granddam={lineage.maternal_granddam}
        />
      </div>
    </section>
  )
}

function ParentBranch({ label, parent, grandsire, granddam }) {
  return (
    <div className="rounded-[3px] bg-linen p-3">
      <p className="font-mono text-[9px] uppercase tracking-wider text-rust">
        {label}
      </p>
      <div className="mt-0.5">
        <GoatRef goat={parent} />
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2 pl-3">
        <GrandRef label="Grandsire" goat={grandsire} />
        <GrandRef label="Granddam" goat={granddam} />
      </div>
    </div>
  )
}

function GoatRef({ goat }) {
  if (!goat) return <span className="text-sm text-leather/60">Unknown</span>
  return (
    <Link
      to={`/goats/${goat.id}`}
      className="cursor-pointer font-mono text-sm text-clay hover:underline"
    >
      {goat.tag_number}
      {goat.name ? <span className="text-leather"> — {goat.name}</span> : null}
    </Link>
  )
}

function GrandRef({ label, goat }) {
  return (
    <div>
      <p className="font-mono text-[8px] uppercase tracking-wider text-rust/70">
        {label}
      </p>
      <GoatRef goat={goat} />
    </div>
  )
}
