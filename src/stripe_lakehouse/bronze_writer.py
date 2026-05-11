"""Bronze-layer Parquet writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


BRONZE_COLUMNS = [
    "entity",
    "object_id",
    "object_type",
    "raw_payload",
    "source",
    "load_id",
    "extracted_at",
    "stripe_created_at",
]


def build_bronze_rows(
    entity: str,
    records: list[dict[str, Any]],
    load_id: str,
    extracted_at: datetime | None = None,
) -> list[dict[str, Any]]:
    """Wrap raw Stripe records with lakehouse audit metadata."""

    extracted_at = extracted_at or datetime.now(timezone.utc)
    return [
        {
            "entity": entity,
            "object_id": record.get("id"),
            "object_type": record.get("object"),
            "raw_payload": json.dumps(record, sort_keys=True),
            "source": "stripe",
            "load_id": load_id,
            "extracted_at": extracted_at.isoformat(),
            "stripe_created_at": record.get("created"),
        }
        for record in records
    ]


def write_bronze_parquet(base_dir: Path, entity: str, rows: list[dict[str, Any]], load_id: str) -> Path | None:
    """Write Bronze rows to an immutable Parquet file partitioned by entity and date."""

    if not rows:
        return None

    now = datetime.now(timezone.utc)
    output_dir = base_dir / entity / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{load_id}.parquet"

    pd.DataFrame(rows, columns=BRONZE_COLUMNS).to_parquet(output_path, index=False)
    return output_path

