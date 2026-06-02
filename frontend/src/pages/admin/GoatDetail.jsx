import { useParams } from 'react-router-dom'

import PagePlaceholder from '@/components/shared/PagePlaceholder'

export default function GoatDetail() {
  const { uuid } = useParams()
  return (
    <PagePlaceholder eyebrow="Goat" title="Goat detail">
      Full profile, lineage tree, health history, and QR printing arrive in
      Phases 2–4. Routed UUID: <span className="font-mono">{uuid}</span>
    </PagePlaceholder>
  )
}
