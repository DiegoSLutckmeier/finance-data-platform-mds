"""Extract Stripe payment intents."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "scripts"))

import extract_entity


if __name__ == "__main__":
    extract_entity.load_entity("payment_intents")
