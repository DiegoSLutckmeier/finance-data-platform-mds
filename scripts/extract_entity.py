"""Command-line entrypoint for extracting one Stripe entity."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse.extraction.extract_entity import load_entity
from stripe_lakehouse.extraction.strategies import ENTITIES


def main() -> None:
    args = parse_args()
    summary = load_entity(args.entity)
    print_summary(summary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract one Stripe entity into Bronze.")
    parser.add_argument("entity", choices=sorted(ENTITIES))
    return parser.parse_args()


def print_summary(summary: dict) -> None:
    print(f"Entity: {summary['entity']}")
    print(f"Status: {summary['status']}")
    print(f"Rows loaded: {summary['rows_loaded']}")
    print(f"Bronze file: {summary['output_path']}")


if __name__ == "__main__":
    main()
