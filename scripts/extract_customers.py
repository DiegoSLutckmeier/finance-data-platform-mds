"""Extract Stripe customers using small helper modules."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse import bronze_writer, config, state, stripe_client


def main() -> None:
    """Run a full refresh of Stripe customers into Bronze."""

    load_dotenv()
    settings = config.load_settings()
    stripe_client.configure_stripe(settings.stripe_api_key)

    entity = "customers"
    load_id = str(uuid.uuid4())

    customers = list(stripe_client.iter_list_entity(entity, created_gte=None))

    bronze_rows = bronze_writer.build_bronze_rows(
        entity=entity,
        records=customers,
        load_id=load_id,
    )
    output_path = bronze_writer.write_bronze_parquet(
        base_dir=settings.bronze_dir,
        entity=entity,
        rows=bronze_rows,
        load_id=load_id,
    )

    state_data = state.load_state(settings.state_path)
    state.update_entity_state(
        state=state_data,
        entity=entity,
        last_created=None,
        load_id=load_id,
    )
    state_data[entity]["refresh_method"] = "full_refresh"
    state_data[entity]["rows_loaded"] = len(bronze_rows)
    state_data[entity]["last_output_path"] = str(output_path) if output_path else None
    state.save_state(settings.state_path, state_data)

    print(f"Loaded {len(bronze_rows)} customers")
    print(f"Bronze file: {output_path}")
    print(f"State file: {settings.state_path}")


if __name__ == "__main__":
    main()
