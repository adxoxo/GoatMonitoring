import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-svh max-w-[420px] flex-col items-center justify-center px-4 text-center">
      <p className="font-mono text-[11px] uppercase tracking-wider text-rust">
        404
      </p>
      <h1 className="mt-1 font-heading text-2xl font-bold text-soil">
        Page not found
      </h1>
      <Link
        to="/dashboard"
        className="mt-4 font-mono text-xs uppercase tracking-wider text-clay underline underline-offset-4"
      >
        Back to dashboard
      </Link>
    </main>
  )
}
