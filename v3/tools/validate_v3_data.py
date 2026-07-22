#!/usr/bin/env python3
"""Validate core Pleiades V3 JSON data packs without external dependencies."""
from __future__ import annotations
import json
from pathlib import Path
import re
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

def validate_wmi(data: dict) -> None:
    brands = data.get("brands")
    sources = data.get("sources")
    if not isinstance(brands, list):
        ERRORS.append("wmi.json: brands must be an array")
        return
    if len(brands) < 70:
        ERRORS.append(f"wmi.json: expected broad Australian make coverage, found {len(brands)}")
    if not isinstance(sources, list) or len(sources) < 2:
        ERRORS.append("wmi.json: official source register is incomplete")
    names: set[str] = set()
    for i, row in enumerate(brands, 1):
        label = f"wmi.brands[{i}]"
        brand = row.get("brand")
        if not brand:
            ERRORS.append(f"{label}: missing brand")
        elif brand.casefold() in names:
            ERRORS.append(f"{label}: duplicate brand {brand}")
        else:
            names.add(brand.casefold())
        if not row.get("status"):
            ERRORS.append(f"{label}: missing Australian coverage status")
        if not isinstance(row.get("aliases", []), list):
            ERRORS.append(f"{label}: aliases must be an array")
        wmis = row.get("wmis")
        if not isinstance(wmis, list):
            ERRORS.append(f"{label}: wmis must be an array")
            continue
        for wmi in wmis:
            if not isinstance(wmi, str) or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{3}", wmi):
                ERRORS.append(f"{label}: invalid WMI {wmi!r}")
        portal = row.get("portal")
        if portal and not portal.startswith("../"):
            ERRORS.append(f"{label}: portal must be a relative site link")

def validate_vin_prefixes(data: dict, known_brands: set[str]) -> None:
    rules = data.get("rules")
    if not isinstance(rules, list):
        ERRORS.append("vin-prefixes.json: rules must be an array")
        return
    seen: set[tuple[str, str]] = set()
    for i, row in enumerate(rules, 1):
        label = f"vin-prefixes.rules[{i}]"
        prefix = row.get("prefix")
        if not isinstance(prefix, str) or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{1,17}", prefix):
            ERRORS.append(f"{label}: invalid prefix {prefix!r}")
        key = (prefix or "", row.get("label") or "")
        if key in seen:
            ERRORS.append(f"{label}: duplicate prefix/label {key}")
        seen.add(key)
        brand = row.get("brand")
        if brand and brand.casefold() not in known_brands:
            ERRORS.append(f"{label}: brand {brand!r} is not in wmi.json")

def validate_identifiers(data: dict, known_brands: set[str]) -> None:
    rows = data.get("identifiers")
    if not isinstance(rows, list):
        ERRORS.append("identifiers.json: identifiers must be an array")
        return
    if len(rows) < 1:
        ERRORS.append("identifiers.json: at least one confirmed identifier is required")
    ids: set[str] = set()
    values: set[str] = set()
    allowed_types = {"australian-surrogate-vin", "japanese-chassis-number"}
    for i, row in enumerate(rows, 1):
        label = f"identifiers[{i}]"
        rid = row.get("id")
        value = row.get("identifier")
        if not rid or rid in ids:
            ERRORS.append(f"{label}: missing or duplicate id {rid!r}")
        ids.add(rid)
        if not isinstance(value, str) or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{8,17}", value):
            ERRORS.append(f"{label}: invalid identifier {value!r}")
        elif value in values:
            ERRORS.append(f"{label}: duplicate identifier {value}")
        values.add(value)
        if row.get("type") not in allowed_types:
            ERRORS.append(f"{label}: unsupported type {row.get('type')!r}")
        brand = str(row.get("brand", ""))
        if brand.casefold() not in known_brands:
            ERRORS.append(f"{label}: brand {brand!r} is not in wmi.json")
        for related in [row.get("linkedIdentifier"), *(row.get("aliases") or [])]:
            if related and (not isinstance(related, str) or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{8,17}", related)):
                ERRORS.append(f"{label}: invalid related identifier {related!r}")

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
    wmi = load("wmi.json")
    validate_wmi(wmi)
    known_brands = {str(row.get("brand", "")).casefold() for row in wmi.get("brands", [])}
    vehicles = load("vehicles.json")
    validate_vehicles(vehicles)
    for i, vehicle in enumerate(vehicles.get("vehicles", []), 1):
        if str(vehicle.get("brand", "")).casefold() not in known_brands:
            ERRORS.append(f"vehicles[{i}]: brand {vehicle.get('brand')!r} is not in wmi.json")
    validate_vin_prefixes(load("vin-prefixes.json"), known_brands)
    validate_identifiers(load("identifiers.json"), known_brands)
    validate_modules(load("modules.json"))
    if ERRORS:
        print("V3 validation failed:")
        print("\n".join(f"- {item}" for item in ERRORS))
        return 1
    print("Pleiades V3 data validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
