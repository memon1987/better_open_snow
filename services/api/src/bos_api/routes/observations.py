from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..deps import get_firestore_client
from ..models.observation import Observations, SnotelObservation

router = APIRouter(tags=["observations"])


@router.get("/resorts/{resort_id}/observations", response_model=Observations)
def get_observations(resort_id: str) -> Observations:
    db = get_firestore_client()
    resort_snap = db.collection("resorts").document(resort_id).get()
    if not resort_snap.exists:
        raise HTTPException(status_code=404, detail=f"resort '{resort_id}' not found")

    snotel_snap = (
        db.collection("resorts")
        .document(resort_id)
        .collection("snotel")
        .document("latest")
        .get()
    )
    snotel_data = snotel_snap.to_dict() if snotel_snap.exists else None

    snotel_obs = (
        SnotelObservation(
            station_triplet=snotel_data.get("station_triplet", ""),
            observed_at=snotel_data.get("observed_at", ""),
            swe_in=snotel_data.get("swe_in"),
            snow_depth_in=snotel_data.get("snow_depth_in"),
            snow_24h_in=snotel_data.get("snow_24h_in"),
            air_temp_f=snotel_data.get("air_temp_f"),
        )
        if snotel_data
        else None
    )

    return Observations(
        resort_id=resort_id,
        snotel=snotel_obs,
        is_demo=bool((snotel_data or {}).get("_demo", False)),
    )
