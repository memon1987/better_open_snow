# Better Open Snow

Free, mobile-first snow & weather tracker for Epic + Ikon resorts. v0 MVP
covers 5 flagship mountains using only public data (NWS, Open-Meteo, NRCS
SNOTEL). See the PRD for the full scope and `/root/.claude/plans/` for the
build plan.

## Stack

- **Frontend:** Expo (React Native Web) + expo-router, delivered as a PWA
- **API:** FastAPI on Python 3.11, talks to Firestore
- **Ingest:** Python workers pulling NWS + Open-Meteo + SNOTEL
- **Data:** Firestore (emulator locally, Cloud Firestore later)
- **Monorepo:** pnpm + turbo for TS, uv workspace for Python, Makefile on top

## Prereqs

- Node 22 (see `.nvmrc`)
- pnpm 10
- Python 3.11 (see `.python-version`)
- [uv](https://github.com/astral-sh/uv)
- Java 17+ (required by the Firestore emulator — `firebase-tools` is installed via pnpm)

## Quick start

```bash
cp .env.example .env
make install          # pnpm install + uv sync

# Terminal 1
make emulator         # Firestore emulator on :8080, UI on http://localhost:4000
```

Once later milestones land:

```bash
# Terminal 2
make seed && make ingest-once && make backfill-daily

# Terminal 3
make api              # http://localhost:8000
curl localhost:8000/resorts | jq

# Terminal 4
make web              # http://localhost:8081
```

## Milestone status

- [x] **M0** — Repo skeleton, emulator boots
- [x] **M1** — FastAPI hello-world
- [ ] **M2** — Seed 5 resorts
- [ ] **M3** — `/resorts` endpoints
- [ ] **M4** — Open-Meteo ingest
- [ ] **M5** — NWS ingest
- [ ] **M6** — SNOTEL ingest
- [ ] **M7** — Daily aggregator + backfill
- [ ] **M8** — Forecast / observations / history endpoints
- [ ] **M9** — Expo web shell
- [ ] **M10** — Detail page wired up
- [ ] **M11** — Polish

## Layout

```
apps/web              Expo + expo-router PWA
services/api          FastAPI service (Cloud Run target)
services/ingest       Data ingest workers (Cloud Run Jobs target)
packages/shared       resorts.seed.json, openapi.json, generated TS types
```

## Non-goals (v0)

No resort scraping, grooming, favorites, comparison view, push notifications,
user accounts, YoY historicals, native iOS/Android builds, or GCP deploy.
