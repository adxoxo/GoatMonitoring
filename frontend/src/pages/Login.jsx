import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useLogin } from '@/hooks/useAuth'

// Admin login. Posts to the JWT endpoint, stores the token, and lands on the
// dashboard. Worker QR-scan pages are public and never reach here.
export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const loginMutation = useLogin()

  function handleSubmit(event) {
    event.preventDefault()
    loginMutation.mutate(
      { username, password },
      { onSuccess: () => navigate('/dashboard') },
    )
  }

  return (
    <main className="grid min-h-svh place-items-center bg-paper px-4">
      <div className="w-full max-w-[360px]">
        <div className="font-heading text-2xl font-bold leading-tight text-soil">
          Goated<span className="text-clay">Tracking</span>
        </div>
        <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-rust">
          Farm OS v1.0 — admin sign in
        </p>

        <form
          onSubmit={handleSubmit}
          className="mt-6 rounded-[3px] border border-leather/20 bg-linen p-5"
        >
          <label
            htmlFor="username"
            className="block font-mono text-[10px] uppercase tracking-wider text-rust"
          >
            Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 min-h-[44px] w-full rounded-[3px] border border-leather/30 bg-paper px-3 text-sm text-soil"
          />

          <label
            htmlFor="password"
            className="mt-4 block font-mono text-[10px] uppercase tracking-wider text-rust"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 min-h-[44px] w-full rounded-[3px] border border-leather/30 bg-paper px-3 text-sm text-soil"
          />

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="mt-6 min-h-[44px] w-full cursor-pointer rounded-[3px] bg-clay px-3 font-mono text-[11px] uppercase tracking-wide text-paper hover:bg-clay/90 disabled:opacity-50"
          >
            {loginMutation.isPending ? 'Signing in…' : 'Sign in'}
          </button>

          {loginMutation.isError && (
            <p role="alert" className="mt-3 font-mono text-[11px] text-alert">
              Incorrect username or password.
            </p>
          )}
        </form>
      </div>
    </main>
  )
}
