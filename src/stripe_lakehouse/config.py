"""Configuration helpers for the Stripe lakehouse pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    stripe_api_key: str
    data_dir: Path
    state_path: Path
    duckdb_path: Path
    lookback_days: int = 2

    @property
    def bronze_dir(self) -> Path:
        return self.data_dir / "bronze" / "stripe"


def load_settings() -> Settings:
    """Load settings from environment variables with local-friendly defaults."""

    data_dir = Path(os.getenv("LAKEHOUSE_DATA_DIR", "./data"))
    return Settings(
        stripe_api_key=_required_env("STRIPE_API_KEY"),
        data_dir=data_dir,
        state_path=Path(
            os.getenv("STRIPE_STATE_PATH", str(data_dir / "state" / "stripe_state.json"))
        ),
        duckdb_path=Path(os.getenv("DUCKDB_PATH", str(data_dir / "finance_lakehouse.duckdb"))),
        lookback_days=int(os.getenv("STRIPE_LOOKBACK_DAYS", "2")),
    )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

