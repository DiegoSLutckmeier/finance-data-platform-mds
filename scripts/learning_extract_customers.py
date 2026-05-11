"""Temporary learning script: extract Stripe customers into Bronze Parquet.

This file intentionally keeps the main flow in one place so it is easier to
read while learning. Later, we can delete it and use the modular package code.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import stripe
from dotenv import load_dotenv


def main() -> None:
    """Run a full refresh of Stripe customers into the Bronze layer."""

    load_dotenv()

    stripe.api_key = os.environ["STRIPE_API_KEY"]

    data_dir = Path(os.getenv("LAKEHOUSE_DATA_DIR", "./data"))
    bronze_dir = data_dir / "bronze" / "stripe" / "customers"
    state_path = data_dir / "state" / "stripe_state.json"

    load_id = str(uuid.uuid4())
    extracted_at = datetime.now(timezone.utc)

    customers = []
    for customer in stripe.Customer.list(limit=100).auto_paging_iter():
        customers.append(dict(customer))

    bronze_rows = []
    for customer in customers:
        bronze_rows.append(
            {
                "entity": "customers",
                "object_id": customer.get("id"),
                "object_type": customer.get("object"),
                "raw_payload": json.dumps(customer, sort_keys=True),
                "source": "stripe",
                "load_id": load_id,
                "extracted_at": extracted_at.isoformat(),
                "stripe_created_at": customer.get("created"),
            }
        )

    output_dir = bronze_dir / f"{extracted_at:%Y}" / f"{extracted_at:%m}" / f"{extracted_at:%d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{load_id}.parquet"

    pd.DataFrame(bronze_rows).to_parquet(output_path, index=False)

    state = {
        "customers": {
            "refresh_method": "full_refresh",
            "last_successful_sync": datetime.now(timezone.utc).isoformat(),
            "last_load_id": load_id,
            "last_output_path": str(output_path),
            "rows_loaded": len(bronze_rows),
        }
    }

    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, sort_keys=True)
        file.write("\n")

    print(f"Loaded {len(bronze_rows)} customers")
    print(f"Bronze file: {output_path}")
    print(f"State file: {state_path}")


if __name__ == "__main__":
    main()
