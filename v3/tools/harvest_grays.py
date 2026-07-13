#!/usr/bin/env python3
"""Harvest public Australian vehicle fields from queued Grays lot pages.

The script renders each lot with Playwright, extracts JSON-LD plus visible text,
normalises VIN candidates, and writes review records. It never promotes a VIN
fingerprint automatically; confirmed records still require specification review.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VIN_RE = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
YEAR_RE = re.compile(r"\b(19[89]\d|20[0-3]\d)\b")
FIELD_PATTERNS = {
    "vin": [r"\bVIN\b\s*[:\-]?\s*([A-HJ-NPR-Z0-9]{17})", r"Vehicle Identification Number\s*[:\-]?\s*([A-HJ-NPR-Z0-9]{17})"],
    "engineCc": [r"Engine(?: Size| Capacity)?\s*[:\-]?\s*([0-9,]{3,5})\s*cc", r"([0-9,]{3,5})\s*cc"],
    "powerKw": [r"Power\s*[:\-]?\s*(\d{2,3})\s*kW", r"(\d{2,3})\s*kW"],
    "transmission": [r"Transmission\s*[:\-]?\s*([^\n\r|]{3,80})"],
    "buildDate": [r"Build Date\s*[:\-]?\s*([^\n\r|]{3,40})"],
    "complianceDate": [r"Compliance(?: Date)?\s*[:\-]?\s*([^\n\r|]{3,40})"],
}


def first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return None


def flatten_json(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(flatten_json(v) for v in value.values())
    if isinstance(value, list):
        return "\n".join(flatten_json(v) for v in value)
    return "" if value is None else str(value)


def normalise_vin(value: str | None) -> str | None:
    if not value:
        return None
    candidate = re.sub(r"[^A-Z0-9]", "", value.upper())
    if len(candidate) == 17 and VIN_RE.fullmatch(candidate):
        return candidate
    return None


async def scrape_one(browser, source: dict[str, Any]) -> dict[str, Any]:
    page = await browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        viewport={"width": 1440, "height": 1200},
    )
    result: dict[str, Any] = {
        "sourceId": source["id"],
        "sourceUrl": source["url"],
        "brand": source.get("brand"),
        "titleHint": source.get("titleHint"),
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "status": "manual-review",
        "confidence": "unconfirmed",
    }
    try:
        response = await page.goto(source["url"], wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(7000)
        result["httpStatus"] = response.status if response else None
        result["resolvedUrl"] = page.url
        result["pageTitle"] = await page.title()
        body_text = await page.locator("body").inner_text(timeout=20000)
        json_ld_texts = await page.locator('script[type="application/ld+json"]').all_text_contents()
        json_ld: list[Any] = []
        for raw in json_ld_texts:
            try:
                json_ld.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        combined = "\n".join([body_text, flatten_json(json_ld)])
        vin_candidates = sorted({normalise_vin(v) for v in VIN_RE.findall(combined)} - {None})
        explicit_vin = normalise_vin(first_match(combined, FIELD_PATTERNS["vin"]))
        result["vinCandidates"] = vin_candidates
        result["vin"] = explicit_vin or (vin_candidates[0] if len(vin_candidates) == 1 else None)
        result["engineCc"] = first_match(combined, FIELD_PATTERNS["engineCc"])
        result["powerKw"] = first_match(combined, FIELD_PATTERNS["powerKw"])
        result["transmissionText"] = first_match(combined, FIELD_PATTERNS["transmission"])
        result["buildDateText"] = first_match(combined, FIELD_PATTERNS["buildDate"])
        result["complianceDateText"] = first_match(combined, FIELD_PATTERNS["complianceDate"])
        years = sorted(set(YEAR_RE.findall(f"{result['pageTitle']}\n{body_text[:10000]}")))
        result["yearCandidates"] = years
        result["evidence"] = {
            "title": result["pageTitle"],
            "visibleTextExcerpt": body_text[:5000],
            "jsonLd": json_ld,
        }
        if result["vin"]:
            result["status"] = "vin-found-review-required"
            result["confidence"] = "public-vin-observed"
        elif response and response.status >= 400:
            result["status"] = "blocked-or-unavailable"
        else:
            result["status"] = "no-public-vin-found"
    except Exception as exc:  # noqa: BLE001
        result["status"] = "fetch-error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        await page.close()
    return result


async def run(queue_path: Path, output_path: Path, headed: bool) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit("Install dependencies: pip install playwright && playwright install chromium") from exc

    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    sources = [s for s in queue.get("sources", []) if s.get("status") in {"queued", "retry"}]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headed)
        results = []
        for source in sources:
            print(f"Harvesting {source['id']} ...", flush=True)
            results.append(await scrape_one(browser, source))
        await browser.close()
    payload = {
        "market": "Australia",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "promotionRule": "Never add a VIN fingerprint automatically. Verify Australian delivery, exact variant and powertrain first.",
        "records": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} review records to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=Path("v3/data/source-queue.json"))
    parser.add_argument("--output", type=Path, default=Path("v3/data/source-review.json"))
    parser.add_argument("--headed", action="store_true", help="Show Chromium for sites that challenge headless browsers.")
    args = parser.parse_args()
    asyncio.run(run(args.queue, args.output, args.headed))


if __name__ == "__main__":
    main()
