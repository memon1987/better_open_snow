"""CLI: write FastAPI's OpenAPI schema to packages/shared/openapi.json.

Usage: `python -m bos_api.dump_openapi`
"""

import json
from pathlib import Path

from .main import app


def main() -> None:
    # services/api/src/bos_api/dump_openapi.py  →  repo root is 5 levels up
    repo_root = Path(__file__).resolve().parents[4]
    target = repo_root / "packages" / "shared" / "openapi.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    target.write_text(json.dumps(schema, indent=2) + "\n")
    print(f"Wrote {target.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
