"""Firestore client + document helpers shared across ingest jobs."""

from __future__ import annotations

import os
from functools import lru_cache

from google.cloud import firestore


@lru_cache(maxsize=1)
def get_client() -> firestore.Client:
    """Return a cached Firestore client.

    Honors FIRESTORE_EMULATOR_HOST — when set, the google-cloud-firestore
    library routes all RPCs to the local emulator.
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "demo-bos")
    return firestore.Client(project=project)


def resort_doc(resort_id: str) -> firestore.DocumentReference:
    return get_client().collection("resorts").document(resort_id)


def forecast_snapshot_doc(resort_id: str, source: str) -> firestore.DocumentReference:
    """resorts/{id}/forecast_snapshots/{nws|open_meteo} — one doc per source."""
    return resort_doc(resort_id).collection("forecast_snapshots").document(source)


def snotel_latest_doc(resort_id: str) -> firestore.DocumentReference:
    return resort_doc(resort_id).collection("snotel").document("latest")


def snotel_obs_collection(resort_id: str) -> firestore.CollectionReference:
    return resort_doc(resort_id).collection("snotel_obs")


def daily_snow_collection(resort_id: str) -> firestore.CollectionReference:
    return resort_doc(resort_id).collection("daily_snow")
