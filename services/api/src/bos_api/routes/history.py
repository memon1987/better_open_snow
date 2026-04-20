from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException

from ..deps import get_firestore_client
from ..models.history import DailySnow, History

router = APIRouter(tags=["history"])


def _current_season_start() -> date:
    today = datetime.now(timezone.utc).date()
    year = today.year if today.month >= 10 else today.year - 1
    return date(year, 10, 1)


@router.get("/resorts/{resort_id}/history", response_model=History)
def get_history(resort_id: str) -> History:
    db = get_firestore_client()
    resort_snap = db.collection("resorts").document(resort_id).get()
    if not resort_snap.exists:
        raise HTTPException(status_code=404, detail=f"resort '{resort_id}' not found")

    season_start = _current_season_start()
    daily_col = (
        db.collection("resorts").document(resort_id).collection("daily_snow")
    )

    docs = list(daily_col.stream())
    daily: list[DailySnow] = []
    total = 0.0
    for d in docs:
        data = d.to_dict() or {}
        if not data.get("date") or data["date"] < season_start.isoformat():
            continue
        snow = data.get("snow_in_24h") or 0.0
        total += float(snow)
        daily.append(
            DailySnow(
                date=data["date"],
                snow_in_24h=data.get("snow_in_24h"),
                snow_depth_in=data.get("snow_depth_in"),
                swe_in=data.get("swe_in"),
                temp_hi_f=data.get("temp_hi_f"),
                temp_lo_f=data.get("temp_lo_f"),
                source=data.get("source"),
            )
        )

    daily.sort(key=lambda x: x.date)
    return History(
        resort_id=resort_id,
        season_start=season_start.isoformat(),
        season_to_date_in=round(total, 1),
        daily=daily,
    )
