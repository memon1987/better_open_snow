import os
from functools import lru_cache

from google.cloud import firestore


@lru_cache(maxsize=1)
def get_firestore_client() -> firestore.Client:
    """Return a Firestore client.

    Honors FIRESTORE_EMULATOR_HOST — when set, google-cloud-firestore
    routes all traffic to the local emulator and uses anonymous credentials.
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "demo-bos")
    return firestore.Client(project=project)
