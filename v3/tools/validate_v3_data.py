#!/usr/bin/env python3
"""Validate core Pleiades V3 JSON data packs without external dependencies."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

def load(name: str) -> dict:
    path = ROOT / "data" / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"{path}: {exc}")
        return {}

def validate_vehicles(data: dict) -> None:
    rows = data.get("vehicles")
    if not isinstance(rows, list):
        ERRORS.append("vehicles.json: vehicles must be an array")
        return
    ids: set[str] = set()
    prefixes: dict[str, str] = {}
    for i, row in enumerate(rows, 1):
        label = f"vehicles[{i}]"
        for field in ("id", "brand", "year", "model", "variant", "vinPrefixes"):
            if not row.get(field):
                ERRORS.append(f"{label}: missing {field}")
        rid = row.get("id")
        if rid in ids:
            ERRORS.append(f"{label}: duplicate id {rid}")
        ids.add(rid)
        for prefix in row.get("vinPrefixes", []):
            if not isinstance(prefix, str) or len(prefix) < 8:
                ERRORS.append(f"{label}: invalid VIN prefix {prefix!r}")
            if prefix in prefixes and prefixes[prefix] != rid:
                ERRORS.append(f"{label}: VIN prefix {prefix} also belongs to {prefixes[prefix]}")
            prefixes[prefix] = rid
        weight = row.get("kerbWeightKg")
        power = (row.get("engine") or {}).get("powerKw")
        if weight is not None and (not isinstance(weight, (int, float)) or weight <= 0):
            ERRORS.append(f"{label}: invalid kerb weight")
        if power is not None and (not isinstance(power, (int, float)) or power <= 0):
            ERRORS.append(f"{label}: invalid power")

def validate_modules(data: dict) -> None:
    rows = data.get("modules")
    if not isinstance(rows, list):
        ERRORS.append("modules.json: modules must be an array")
        return
    for i, row in enumerate(rows, 1):
        for field in ("name", "type", "status", "href"):
            if not row.get(field):
                ERRORS.append(f"modules[{i}]: missing {field}")

def main() -> int:
    validate_vehicles(load("vehicles.json"))
    validate_modules(load("modules.json"))
    if ERRORS:
        print("V3 validation failed:")
        print("\n".join(f"- {item}" for item in ERRORS))
        return 1
    print("Pleiades V3 data validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
