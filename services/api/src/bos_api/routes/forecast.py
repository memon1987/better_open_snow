from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..deps import get_firestore_client
from ..models.forecast import DailyPoint, Forecast, HourlyPoint

router = APIRouter(tags=["forecast"])


@router.get("/resorts/{resort_id}/forecast", response_model=Forecast)
def get_forecast(resort_id: str) -> Forecast:
    db = get_firestore_client()
    resort_snap = db.collection("resorts").document(resort_id).get()
    if not resort_snap.exists:
        raise HTTPException(status_code=404, detail=f"resort '{resort_id}' not found")

    om_snap = (
        db.collection("resorts")
        .document(resort_id)
        .collection("forecast_snapshots")
        .document("open_meteo")
        .get()
    )
    if not om_snap.exists:
        raise HTTPException(
            status_code=503,
            detail="no forecast data — run `make ingest-open-meteo`",
        )
    om = om_snap.to_dict() or {}

    return Forecast(
        resort_id=resort_id,
        generated_at=om.get("fetched_at", ""),
        hourly=[HourlyPoint(**p) for p in om.get("hourly", [])],
        daily=[DailyPoint(**p) for p in om.get("daily", [])],
        sources={"snow": "open_meteo", "narrative": "open_meteo"},
        is_demo=bool(om.get("_demo", False)),
    )
