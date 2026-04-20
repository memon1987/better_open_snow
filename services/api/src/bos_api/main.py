from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .deps import get_firestore_client
from .routes import resorts as resorts_routes

app = FastAPI(
    title="Better Open Snow API",
    version="0.0.0",
    description="Snow + weather data for Epic/Ikon resorts (v0 MVP)",
)

# Permissive CORS for local dev — the Expo web client on :8081 and
# phone-on-LAN browsers need to reach this API. Tighten before prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(resorts_routes.router)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/debug/firestore-ping")
def firestore_ping() -> dict[str, str]:
    db = get_firestore_client()
    doc_ref = db.collection("_debug").document("ping")
    now = datetime.now(timezone.utc).isoformat()
    doc_ref.set({"at": now})
    snapshot = doc_ref.get()
    return {"at": snapshot.get("at")}
