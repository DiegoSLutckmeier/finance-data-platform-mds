"""Run entity extractors one table at a time."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "scripts"))

import extract_entity


ENTITIES = [
    "customers",
    "charges",
]


def main() -> None:
    results = []

    for entity in ENTITIES:
        print(f"\nStarting {entity}")
        try:
            result = extract_entity.load_entity(entity)
        except Exception as exc:
            result = {
                "entity": entity,
                "status": "failed",
                "error": str(exc),
            }
            print(f"Failed {entity}: {exc}")

        results.append(result)

    print("\nExtraction summary")
    for result in results:
        print(f"- {result['entity']}: {result['status']}")

    failed = [result for result in results if result["status"] != "success"]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
