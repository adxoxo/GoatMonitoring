import { NavLink, Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  IconLayoutDashboard,
  IconListDetails,
  IconFence,
  IconHeartbeat,
  IconLogout,
} from '@tabler/icons-react'

import { isAuthenticated, logout } from '@/hooks/useAuth'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: IconLayoutDashboard },
  { to: '/goats', label: 'Goats', icon: IconListDetails },
  { to: '/areas', label: 'Areas', icon: IconFence },
  { to: '/health', label: 'Health', icon: IconHeartbeat },
]

// Subtle film-grain (feTurbulence) — gives the --bark surfaces depth, not flat.
const GRAIN =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")"

const TITLES = {
  '/dashboard': 'Dashboard',
  '/goats': 'Goats',
  '/areas': 'Areas',
  '/health': 'Health Records',
}

function pageTitle(pathname) {
  const key = Object.keys(TITLES).find(
    (k) => pathname === k || pathname.startsWith(k + '/'),
  )
  return TITLES[key] ?? 'GoatedTracking'
}

function sidebarItemClass({ isActive }) {
  const base =
    'flex items-center gap-2.5 px-4 py-2.5 font-body text-[12.5px] cursor-pointer border-l-2 border-r-2 transition-colors'
  return isActive
    ? `${base} border-l-clay border-r-clay bg-clay/[0.18] text-straw`
    : `${base} border-l-transparent border-r-transparent text-straw/60 hover:text-straw hover:bg-clay/[0.08]`
}

function tabItemClass({ isActive }) {
  const base =
    'flex flex-1 flex-col items-center gap-1 py-2.5 font-mono text-[9px] uppercase tracking-wide cursor-pointer'
  return isActive ? `${base} text-clay` : `${base} text-straw/55`
}

export default function AppShell() {
  const location = useLocation()
  const navigate = useNavigate()

  // Admin pages require a token; worker QR pages and /login are public.
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-svh md:flex">
      {/* Sidebar — desktop only */}
      <aside className="relative hidden w-[200px] shrink-0 bg-bark md:block">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 opacity-[0.04]"
          style={{ backgroundImage: GRAIN }}
        />
        <div className="relative flex h-full flex-col">
          <div className="px-4 pb-5 pt-6">
            <div className="font-heading text-lg font-bold leading-tight text-straw">
              Goated
              <br />
              Tracking
            </div>
            <div className="mt-1 font-mono text-[9px] uppercase tracking-widest text-wheat/50">
              Farm OS v1.0
            </div>
          </div>

          <nav className="mt-2 flex flex-col">
            <div className="px-4 pb-1.5 font-mono text-[9px] uppercase tracking-widest text-wheat/40">
              Manage
            </div>
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className={sidebarItemClass}>
                <Icon size={16} stroke={1.75} aria-hidden="true" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[52px] shrink-0 items-center justify-between border-b border-leather/15 bg-paper px-5">
          <h1 className="font-heading text-base font-semibold text-soil">
            {pageTitle(location.pathname)}
          </h1>
          <div className="flex items-center gap-4">
            <span className="font-mono text-[10px] uppercase tracking-wider text-rust">
              goatfarm.local
            </span>
            <button
              type="button"
              onClick={handleLogout}
              aria-label="Log out"
              className="flex cursor-pointer items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-leather hover:text-clay"
            >
              <IconLogout size={14} aria-hidden="true" />
              Log out
            </button>
          </div>
        </header>

        {/* extra bottom padding clears the mobile tab bar */}
        <main className="flex-1 px-5 py-6 pb-24 md:pb-6">
          <Outlet />
        </main>
      </div>

      {/* Bottom tab nav — mobile only */}
      <nav className="fixed inset-x-0 bottom-0 z-10 flex border-t border-leather/20 bg-bark md:hidden">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={tabItemClass}>
            <Icon size={20} stroke={1.75} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
