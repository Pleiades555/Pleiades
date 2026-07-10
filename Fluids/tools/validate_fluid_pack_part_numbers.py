#!/usr/bin/env python3
"""Validate fluid pack-size, market and Nissan Matic numbering integrity.

Usage:
    python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/fluids_master.json
    python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/nissan_fluids_import.csv
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys
from collections import defaultdict
from typing import Any


def norm(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "")


def text(value: Any) -> str:
    return str(value or "").strip()


def load_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON root must be an array")
        return [row for row in data if isinstance(row, dict)]
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError("Expected a .json or .csv file")


NISSAN_MATIC_PREFIXES = {
    "KLE22": "MATICD",
    "KLE23": "MATICJ",
    "KLE24": "MATICS",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_fluid_pack_part_numbers.py <fluids.json|fluids.csv>")
        return 2

    path = pathlib.Path(sys.argv[1])
    rows = load_rows(path)
    volumes: dict[tuple[str, str], set[str]] = defaultdict(set)
    duplicate_keys: dict[tuple[str, str, str], int] = defaultdict(int)
    problems = 0

    for line_no, row in enumerate(rows, start=2):
        brand = norm(row.get("brand"))
        part = norm(row.get("part_number"))
        volume = norm(row.get("volume"))
        description = norm(row.get("description"))
        brand_spec = norm(row.get("brand_spec"))

        if brand and part:
            if volume:
                volumes[(brand, part)].add(volume)
            duplicate_keys[(brand, part, volume)] += 1

        if brand == "NISSAN":
            market = text(row.get("market"))
            market_status = text(row.get("market_status"))
            if not market or not market_status:
                problems += 1
                print(f"MARKET LABEL MISSING: line {line_no} NISSAN {part or '[NO PART NUMBER]'}")

            compact_part = re.sub(r"[^A-Z0-9]", "", part)
            for prefix, required_fluid in NISSAN_MATIC_PREFIXES.items():
                if compact_part.startswith(prefix):
                    combined = description + brand_spec
                    if required_fluid not in combined:
                        problems += 1
                        print(
                            f"NISSAN MATIC PREFIX MISMATCH: line {line_no} {part} "
                            f"must describe {required_fluid.replace('MATIC', 'Matic ')}"
                        )
                    if compact_part.endswith("00004") and volume != "4L":
                        problems += 1
                        print(
                            f"NISSAN PACK SUFFIX MISMATCH: line {line_no} {part} "
                            f"ends -00004 but volume is {volume or '[BLANK]'}, expected 4L"
                        )
                    break

    for (brand, part), sizes in sorted(volumes.items()):
        if len(sizes) > 1:
            problems += 1
            print(f"PACK-SIZE CHECK REQUIRED: {brand} {part} appears as {', '.join(sorted(sizes))}")

    for (brand, part, volume), count in sorted(duplicate_keys.items()):
        if count > 1:
            problems += 1
            print(f"DUPLICATE: {brand} {part} {volume or '[NO VOLUME]'} occurs {count} times")

    print(f"Checked {len(rows)} rows; {problems} issue(s) found.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
