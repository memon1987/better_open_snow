.PHONY: help install emulator api web seed ingest-once ingest-nws ingest-open-meteo ingest-snotel backfill-daily openapi dev clean

help:
	@echo "Better Open Snow — dev targets"
	@echo ""
	@echo "  install          Install pnpm + uv dependencies"
	@echo "  emulator         Start Firestore emulator (port 8080, UI 4000)  [M0]"
	@echo "  api              Start FastAPI dev server on :8000              [M1+]"
	@echo "  web              Start Expo web dev server on :8081             [M9+]"
	@echo "  seed             Upsert 5 resorts into Firestore                [M2+]"
	@echo "  ingest-once      Run nws + open_meteo + snotel + aggregator     [M4+]"
	@echo "  backfill-daily   Backfill season-to-date from Open-Meteo archive [M7+]"
	@echo "  openapi          Regenerate packages/shared/openapi.json        [M3+]"
	@echo "  dev              Run emulator + api + web concurrently          [M9+]"
	@echo "  clean            Remove build artifacts and caches"

install:
	pnpm install
	@if [ -d services/api ] || [ -d services/ingest ]; then \
		cd services && uv sync; \
	else \
		echo "No Python services yet — skipping uv sync"; \
	fi

emulator:
	pnpm exec firebase emulators:start --only firestore --project demo-bos

api:
	@echo "api: not implemented until M1"; exit 1

web:
	@echo "web: not implemented until M9"; exit 1

seed:
	@echo "seed: not implemented until M2"; exit 1

ingest-once:
	@echo "ingest-once: not implemented until M4"; exit 1

ingest-nws:
	@echo "ingest-nws: not implemented until M5"; exit 1

ingest-open-meteo:
	@echo "ingest-open-meteo: not implemented until M4"; exit 1

ingest-snotel:
	@echo "ingest-snotel: not implemented until M6"; exit 1

backfill-daily:
	@echo "backfill-daily: not implemented until M7"; exit 1

openapi:
	@echo "openapi: not implemented until M3"; exit 1

dev:
	@echo "dev: not implemented until M9"; exit 1

clean:
	rm -rf node_modules .turbo .pnpm-store
	rm -rf apps/*/node_modules apps/*/.expo apps/*/web-build
	rm -rf packages/*/node_modules packages/*/dist
	rm -rf services/.venv services/**/__pycache__ services/.ruff_cache services/.pytest_cache
	rm -rf .firebase firebase-debug.log firestore-debug.log ui-debug.log
