# GoatedTracking

A local-first goat farm monitoring system for a small farm in the Philippines.
It tracks individual goats, their health records, vaccination schedules, pen
assignments, and lineage. Each goat wears a plastic ear tag printed with a QR
code — scanning it opens that goat's profile instantly in any phone browser on
the farm WiFi. The whole system runs on one on-premise server with **zero cloud
dependencies** for core functionality; the internet is treated as optional.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 LTS + Django REST Framework |
| Database | PostgreSQL 16 |
| Frontend | React 18 + Vite + Tailwind CSS v4 |
| Auth | JWT (admin only); worker QR view is public |
| QR codes | segno (server-side PNG + print PDF) |
| Reverse proxy | Nginx |
| Containers | Docker + Docker Compose |
| Tests | pytest + factory_boy (backend), Vitest + Testing Library (frontend) |

---

## Repository layout

```
goatmontr/
├── backend/                Django project (config/) + domain apps (apps/)
│   ├── config/settings/    base.py · development.py · production.py
│   ├── apps/               goats · health · qr · users
│   └── requirements/       base · development · production
├── frontend/               React + Vite SPA (admin dashboard + worker view)
├── nginx/nginx.conf        reverse proxy (prod)
├── docker-compose.yml      production stack
├── docker-compose.dev.yml  development stack (hot reload)
└── .env.example            environment template
```

---

## Prerequisites

- **Docker + Docker Compose** — the supported way to run the full stack.
- For running pieces directly without Docker: **Python 3.12** and **Node 20+**.

---

## First-time setup

```bash
# 1. Create your env files from the template, then fill in real values
cp .env.example backend/.env       # Django + Postgres settings
cp .env.example frontend/.env      # VITE_ values

# 2. Start the development stack (Django + Vite + Postgres)
docker compose -f docker-compose.dev.yml up --build
```

- Backend  → http://localhost:8000
- Frontend → http://localhost:5173
- Django admin (emergency only) → http://localhost:8000/django-admin/

At minimum set in `backend/.env`: `DJANGO_SECRET_KEY`, `DB_PASSWORD`, and the
matching `POSTGRES_PASSWORD`. See [.env.example](.env.example) for the full list.

### Create the first admin user

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

---

## Running tests

```bash
# Backend (from backend/)
pytest

# Frontend (from frontend/)
npm test
```

Both follow TDD (RED, GREEN, REFACTOR).

Without Docker you can still run the frontend (`npm install && npm run dev`)
and its tests, and the backend test suite/`manage.py check` via a local
virtualenv. Running the backend **server** without Docker additionally requires
a reachable PostgreSQL (the app does not use SQLite).

---

## Production

```bash
# Build and start the full production stack (Nginx on port 80)
docker compose up --build -d
```

The backend entrypoint runs migrations and `collectstatic` automatically, then
starts Gunicorn. Nginx serves the built SPA, proxies `/api/`, and serves
`/media/` (QR images). A UPS on the server is **required**.

### LAN hostname — `goatfarm.local`

So any phone on the farm WiFi can reach the server by name (no router config):

```bash
sudo apt install avahi-daemon
sudo hostnamectl set-hostname goatfarm
# Devices on the LAN can now reach http://goatfarm.local
```

If mDNS is unavailable, use the server's LAN IP directly and add it to
`DJANGO_ALLOWED_HOSTS`.

---

## Phase 0 connectivity checklist

Run these on a machine with Docker to confirm the stack is wired end-to-end:

- [ ] `docker compose up` starts all services with no errors
- [ ] `db` container reports healthy
- [ ] Browser reaches `goatfarm.local` (after avahi setup) and it serves the SPA
- [ ] `goatfarm.local/api/` returns a Django 404 (not an Nginx 404)
- [ ] `goatfarm.local/django-admin/` loads the Django admin login

> These require a Docker host and were **not** verifiable in the scaffold
> environment (Docker not installed there). The backend (`manage.py check` on
> dev + prod settings, `pytest`) and the frontend (`build`, `test`, `dev`
> server) were all verified directly.

---

## Conventions

- Strict five-layer architecture — Presentation → API → Service → Data → Infra.
  Each layer talks only to the one below.
- Conventional commits (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`, `docs:`).
- Python: PEP 8 / Black / isort. JS: ESLint / Prettier.
- The visual design system is **locked**.
