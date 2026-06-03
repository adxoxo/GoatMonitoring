import { IconPrinter, IconQrcode, IconRefresh } from '@tabler/icons-react'

// Admin QR block: preview, UUID, and Print / Regenerate actions.
// Print opens the QR PNG (served publicly via /media/) in a new tab.
export default function QrTagCard({ uuid, qrImageUrl, onRegenerate, isRegenerating = false }) {
  return (
    <section className="rounded-[3px] border border-leather/20 bg-paper p-4">
      <h2 className="font-mono text-[10px] uppercase tracking-wider text-leather">
        QR tag
      </h2>

      <div className="mt-3 flex items-center gap-4">
        <div className="grid size-16 shrink-0 place-items-center rounded-[4px] border border-leather/20 bg-linen">
          {qrImageUrl ? (
            <img src={qrImageUrl} alt="Goat QR tag" className="size-full rounded-[4px]" />
          ) : (
            <IconQrcode size={28} className="text-leather/50" aria-hidden />
          )}
        </div>
        <div className="min-w-0">
          <p className="break-all font-mono text-[9px] text-rust">{uuid}</p>
          {!qrImageUrl && (
            <p className="mt-1 text-xs text-leather">No QR generated yet.</p>
          )}
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <button
          type="button"
          onClick={() => qrImageUrl && window.open(qrImageUrl, '_blank')}
          disabled={!qrImageUrl}
          className="inline-flex cursor-pointer items-center gap-1.5 rounded-[3px] border border-leather/30 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wide text-leather hover:bg-leather/5 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <IconPrinter size={14} aria-hidden /> Print
        </button>
        <button
          type="button"
          onClick={onRegenerate}
          disabled={isRegenerating}
          className="inline-flex cursor-pointer items-center gap-1.5 rounded-[3px] border border-clay/40 bg-clay/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wide text-clay hover:bg-clay/20 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <IconRefresh size={14} aria-hidden />
          {isRegenerating ? 'Regenerating…' : 'Regenerate'}
        </button>
      </div>
    </section>
  )
}
