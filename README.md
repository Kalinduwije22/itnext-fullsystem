# ITNEXT Global Careers — Full System

End-to-end career & global-mobility platform. **Next.js frontend** +
**FastAPI modular-monolith backend** + **PostgreSQL**, containerised and
deployable to Azure Container Apps.

```
itnext/
├── backend/          FastAPI modular monolith (auth, packages, cv,
│                     assessment, chat, payments)
├── frontend/         Next.js 14 App Router + Tailwind
├── docker-compose.yml  db + redis + api1/api2/api3 (behind nginx) + web
├── deploy/nginx.conf   local load balancer, round-robins across the 3 api replicas
├── Makefile          dev + Azure deploy targets
└── .github/workflows/  CI (test/build) + Deploy (make ship)
```

## Run the whole thing locally

```bash
cp .env.example .env
docker compose up -d --build      # db, redis, api1-3 behind nginx (:8000), web (:3000)
make migration m="initial schema"
make migrate
make seed                         # insert the 4 package tiers
```

The API runs as 3 replicas (`api1`/`api2`/`api3`) behind an nginx load balancer
(`deploy/nginx.conf`, `least_conn`), so `http://localhost:8000` is unchanged
from a client's perspective but every request is spread across replicas.

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## The user journey (matches the build)
1. **Landing** (`/`) — hero, 8-service portfolio, 4 packages, the flight-path journey.
2. **Sign up / log in** (`/signup`, `/login`) — JWT stored client-side.
3. **Dashboard** (`/dashboard`) — the profile page:
   - **1 · Choose a package** → creates an order (PayHere checkout stub)
   - **2 · Upload CV** → pre-signed direct-to-blob upload + async parse
   - **3 · Professional profile** → questionnaire saved as JSONB
   - **4 · Career assistant** → Claude-powered chat (no WebSocket needed)

## Design
Navy + teal system grounded in the brand's global-mobility identity:
boarding-pass mono labels, a dotted flight-path connector, Colombo→London
cues. Display **Space Grotesk**, body **Inter**, mono **IBM Plex Mono**.

## Deploy (Azure Container Apps)

```bash
make azure-login
make provision      # one-time: env + app, min 1 / max 5 replicas (load-balanced)
make ship           # build → push → migrate → deploy
```

Or let CI do it: push a `v*` tag and `.github/workflows/deploy.yml` runs `make ship`.

## Intentional stubs (marked TODO in source)
Boots with zero external credentials; wire these when ready:
- CV blob presign → `generate_blob_sas()`
- CV parse → Claude call in `backend/app/modules/cv/service.py`
- Chat → set `ANTHROPIC_API_KEY` for live replies
- PayHere webhook → verify `md5sig` before marking an order paid

## Pricing note
Package prices appear in two places — keep them in sync:
- Backend seed: `backend/app/seed.py`
- Landing marketing copy: `frontend/app/page.tsx` (currently LKR 4,900–19,900)

## Verified
- Backend: health smoke test passes (`make test`).
- Frontend: `tsc --noEmit` passes clean; `npm run build` compiles (needs
  Google Fonts network access, available in CI and normal environments).
