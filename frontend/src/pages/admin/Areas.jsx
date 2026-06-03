import { useAreas, useGoats } from '@/hooks/useAreas'
import TransferForm from '@/components/admin/TransferForm'

export default function Areas() {
  const { data: areas = [], isLoading } = useAreas()
  const { data: goats = [] } = useGoats()

  return (
    <div className="p-6">
      <header>
        <p className="font-mono text-[10px] uppercase tracking-wider text-rust">
          Pens
        </p>
        <h1 className="font-heading text-2xl font-bold text-soil">Areas</h1>
      </header>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {isLoading ? (
            <p className="text-sm text-leather">Loading pens…</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {areas.map((area) => (
                <PenCard key={area.id} area={area} />
              ))}
            </div>
          )}
        </div>
        <div>
          <TransferForm goats={goats} areas={areas} />
        </div>
      </div>
    </div>
  )
}

function PenCard({ area }) {
  const pct = area.capacity
    ? Math.min(100, Math.round((area.goat_count / area.capacity) * 100))
    : 0
  const over = area.goat_count > area.capacity
  return (
    <div className="rounded-[3px] border border-leather/20 bg-linen p-4">
      <h2 className="font-heading text-base font-bold text-soil">{area.name}</h2>
      <p className="mt-1 font-mono text-[11px] text-rust">
        {`${area.goat_count} / ${area.capacity}`}
      </p>
      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-leather/15">
        <div
          className={`h-full ${over ? 'bg-alert' : 'bg-sage'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
