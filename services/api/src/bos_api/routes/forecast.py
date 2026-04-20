from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..deps import get_firestore_client
from ..models.forecast import DailyPoint, Forecast, HourlyPoint, NarrativePeriod
from ..services.forecast_merge import merge

router = APIRouter(tags=["forecast"])


@router.get("/resorts/{resort_id}/forecast", response_model=Forecast)
def get_forecast(resort_id: str) -> Forecast:
    db = get_firestore_client()
    resort_snap = db.collection("resorts").document(resort_id).get()
    if not resort_snap.exists:
        raise HTTPException(status_code=404, detail=f"resort '{resort_id}' not found")

    snapshots_ref = (
        db.collection("resorts").document(resort_id).collection("forecast_snapshots")
    )
    om_snap = snapshots_ref.document("open_meteo").get()
    nws_snap = snapshots_ref.document("nws").get()

    if not om_snap.exists and not nws_snap.exists:
        raise HTTPException(
            status_code=503,
            detail="no forecast data — run `make ingest-once`",
        )

    merged = merge(
        open_meteo=om_snap.to_dict() if om_snap.exists else None,
        nws=nws_snap.to_dict() if nws_snap.exists else None,
    )

    return Forecast(
        resort_id=resort_id,
        generated_at=merged["generated_at"],
        hourly=[HourlyPoint(**p) for p in merged["hourly"]],
        daily=[DailyPoint(**p) for p in merged["daily"]],
        narrative=[NarrativePeriod(**p) for p in merged["narrative"]],
        sources=merged["sources"],
        is_demo=merged["is_demo"],
    )
