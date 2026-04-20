from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..deps import get_firestore_client
from ..models.resort import ResortBase, ResortDetail, ResortElevation, ResortList, ResortSummary

router = APIRouter(tags=["resorts"])


def _summary_from_doc(data: dict, snotel_latest: dict | None) -> ResortSummary:
    base = data.get("base", {})
    summit = data.get("summit", {})
    return ResortSummary(
        resort_id=data["resort_id"],
        name=data["name"],
        **{"pass": data["pass"]},
        state=data["state"],
        base_elevation_ft=base.get("elevation_ft", 0),
        summit_elevation_ft=summit.get("elevation_ft", 0),
        latest_snow_24h_in=(snotel_latest or {}).get("snow_24h_in"),
        snow_depth_in=(snotel_latest or {}).get("snow_depth_in"),
    )


@router.get("/resorts", response_model=ResortList)
def list_resorts() -> ResortList:
    db = get_firestore_client()
    docs = list(db.collection("resorts").stream())

    summaries: list[ResortSummary] = []
    for doc in docs:
        data = doc.to_dict() or {}
        if "resort_id" not in data:
            continue
        snotel_latest_snap = (
            db.collection("resorts")
            .document(doc.id)
            .collection("snotel")
            .document("latest")
            .get()
        )
        snotel_latest = snotel_latest_snap.to_dict() if snotel_latest_snap.exists else None
        summaries.append(_summary_from_doc(data, snotel_latest))

    summaries.sort(key=lambda r: r.name)
    return ResortList(resorts=summaries)


@router.get("/resorts/{resort_id}", response_model=ResortDetail)
def get_resort(resort_id: str) -> ResortDetail:
    db = get_firestore_client()
    snap = db.collection("resorts").document(resort_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail=f"resort '{resort_id}' not found")

    data = snap.to_dict() or {}
    base = data.get("base", {})
    summit = data.get("summit", {})

    return ResortDetail(
        resort_id=data["resort_id"],
        name=data["name"],
        **{"pass": data["pass"]},
        state=data["state"],
        base=ResortBase(
            lat=base.get("lat", 0.0),
            lon=base.get("lon", 0.0),
            elevation_ft=base.get("elevation_ft", 0),
        ),
        summit=ResortElevation(elevation_ft=summit.get("elevation_ft", 0)),
        snotel_triplet=data["snotel_triplet"],
        timezone=data["timezone"],
    )
